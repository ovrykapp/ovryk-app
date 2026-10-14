-- Ovryk, lot 16, livraison 3 : table des sauvegardes en ligne.
-- À coller tel quel dans l'éditeur SQL de Supabase (rôle postgres).
-- Ne contient aucune clé ni aucun mot de passe.
--
-- Une ligne = une sauvegarde complète. payload = le contenu exact d'un
-- fichier d'export Ovryk (enveloppe { app, exportedAt, version, data,
-- summary }), lisible tel quel par l'import de l'app.

create table if not exists public.backups (
  id             uuid primary key default gen_random_uuid(),
  user_id        uuid not null default auth.uid(),
  created_at     timestamptz not null default now(),
  schema_version integer check (schema_version is null or schema_version > 0),
  sessions_count integer not null check (sessions_count >= 0),
  summary        jsonb not null check (jsonb_typeof(summary) = 'object'),
  fingerprint    text not null check (fingerprint ~ '^[0-9a-f]{8}$'),
  payload        text not null,
  -- 2 Mo au plus, en octets (même limite que l'app, CLOUD_BACKUP_MAX_BYTES)
  constraint backups_payload_size check (octet_length(payload) between 2 and 2097152)
);

create index if not exists backups_user_created_idx on public.backups (user_id, created_at desc);

-- RLS activé (pas forcé) : anon et authenticated sont soumis aux politiques ;
-- le propriétaire de la table (postgres), donc la rotation ci-dessous, ne l'est pas.
alter table public.backups enable row level security;

-- Lecture et ajout de ses propres lignes seulement. Aucune politique UPDATE ni DELETE.
drop policy if exists backups_select_own on public.backups;
create policy backups_select_own on public.backups
  for select to authenticated using (user_id = (select auth.uid()));

drop policy if exists backups_insert_own on public.backups;
create policy backups_insert_own on public.backups
  for insert to authenticated with check (user_id = (select auth.uid()));

-- Droits explicites : rien pour anon ni public. authenticated : lecture, et
-- ajout limité aux colonnes utiles (l'app ne peut fixer ni user_id ni created_at).
revoke all on table public.backups from public, anon, authenticated;
grant select on table public.backups to authenticated;
grant insert (id, schema_version, sessions_count, summary, fingerprint, payload)
  on table public.backups to authenticated;

-- Rotation : pour le compte de la ligne ajoutée, garde les 30 plus récentes
-- et la plus complète (plus grand sessions_count, à égalité la plus récente).
-- Ne supprime jamais la ligne qui vient d'être ajoutée, ni la plus complète :
-- il reste donc toujours au moins une sauvegarde.
create or replace function public.backups_rotate()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  delete from public.backups b
  where b.user_id = new.user_id
    and b.id <> new.id
    and b.id not in (
      select r.id from public.backups r
      where r.user_id = new.user_id
      order by r.created_at desc, r.id desc
      limit 30)
    and b.id <> (
      select m.id from public.backups m
      where m.user_id = new.user_id
      order by m.sessions_count desc, m.created_at desc, m.id desc
      limit 1);
  return null;
end;
$$;

revoke all on function public.backups_rotate() from public, anon, authenticated;

drop trigger if exists backups_rotate_after_insert on public.backups;
create trigger backups_rotate_after_insert
  after insert on public.backups
  for each row execute function public.backups_rotate();

-- Rafraîchit le cache de l'API (PostgREST) pour qu'elle voie la table tout de suite.
notify pgrst, 'reload schema';
