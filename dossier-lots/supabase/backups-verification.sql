-- Ovryk, lot 16, livraison 3 : vérifications à lancer à la main après backups.sql.
-- Lecture seule, sauf le test de rotation (section 7), entièrement annulé.

-- 1. RLS activé, non forcé (attendu : relrowsecurity = true, relforcerowsecurity = false)
select relrowsecurity, relforcerowsecurity
from pg_class where oid = 'public.backups'::regclass;

-- 2. Politiques (attendu : exactement deux lignes, backups_select_own SELECT et
--    backups_insert_own INSERT, toutes deux pour {authenticated} ; aucune UPDATE ni DELETE)
select policyname, cmd, roles, qual, with_check
from pg_policies where schemaname = 'public' and tablename = 'backups'
order by policyname;

-- 3. Droits sur la table (attendu : true seulement pour authenticated SELECT ;
--    false partout ailleurs, en particulier UPDATE et DELETE pour authenticated,
--    et tout pour anon)
select r.role, p.priv, has_table_privilege(r.role, 'public.backups', p.priv) as autorise
from (values ('anon'), ('authenticated')) as r(role),
     (values ('SELECT'), ('INSERT'), ('UPDATE'), ('DELETE'), ('TRUNCATE')) as p(priv)
order by 1, 2;

-- 4. Ajout par colonne pour authenticated (attendu : true pour id, schema_version,
--    sessions_count, summary, fingerprint, payload ; false pour user_id et created_at)
select c.column_name, has_column_privilege('authenticated', 'public.backups', c.column_name, 'INSERT') as ajout_autorise
from information_schema.columns c
where c.table_schema = 'public' and c.table_name = 'backups'
order by c.ordinal_position;

-- 5. Fonction de rotation (attendu : prosecdef = true, proconfig = {search_path=""} ;
--    anon_exec = false et auth_exec = false)
select proname, prosecdef, proconfig, pg_get_userbyid(proowner) as proprietaire
from pg_proc where oid = 'public.backups_rotate()'::regprocedure;
select has_function_privilege('anon', 'public.backups_rotate()', 'execute') as anon_exec,
       has_function_privilege('authenticated', 'public.backups_rotate()', 'execute') as auth_exec;

-- 6. Contenu actuel, sans le payload
select count(*) as lignes, max(created_at) as derniere, max(sessions_count) as plus_complete
from public.backups;

-- 7. Test de rotation, SANS TRACE : à lancer seul, en entier (le bloc do $$ ... $$).
--    C'est une transaction qui se termine toujours par une erreur volontaire :
--    l'erreur annule tout (équivalent d'un begin ... rollback), y compris
--    les suppressions de vraies sauvegardes faites par la rotation pendant le
--    test, et son message affiche le résultat (l'éditeur SQL de Supabase
--    n'affiche que le résultat de la dernière instruction, qui serait sinon
--    le rollback).
--    Le bloc insère 35 lignes de test (summary {"test": true}) pour le premier
--    compte de auth.users, de la plus ancienne (n° 1) à la plus récente (n° 35),
--    toutes plus récentes que n'importe quelle vraie sauvegarde :
--      * n° 1 : la plus ancienne, ordinaire (sessions_count = 1001) : doit être supprimée ;
--      * n° 3 : la plus complète (sessions_count = 2147483647, le maximum d'un
--        integer, qu'aucune vraie sauvegarde ne peut dépasser) : plus ancienne que
--        les 30 plus récentes (n° 6 à 35), donc gardée seulement par la règle
--        "garder la plus complète" ;
--      * n° 35 : la plus récente (sessions_count = 1035) : doit être gardée.
--    Les autres lignes ordinaires ont sessions_count = 1000 + leur numéro.
--    Les contrôles ne comptent que les lignes de test, repérées par leur summary,
--    pour qu'une vraie sauvegarde ne les fausse pas.
--    Attendu, dans le message d'erreur "RESULTAT TEST ROTATION" :
--      lignes_restantes = 31 (les 30 plus récentes + la plus complète),
--      lignes_de_test_restantes = 31,
--      plus_complete_gardee = t (la n° 3),
--      plus_recente_gardee = t (la n° 35),
--      plus_ancienne_ordinaire_supprimee = t (la n° 1).
--    Si tu as déjà de vraies sauvegardes en ligne, le résultat reste le même :
--    elles sont plus anciennes que les lignes de test, donc la rotation les
--    supprime aussi pendant le test (n'étant ni parmi les 30 plus récentes ni la
--    plus complète), puis tout est annulé : elles sont intactes après le test.
do $$
declare
  uid uuid;
  restantes integer;
  de_test integer;
  complete_gardee boolean;
  recente_gardee boolean;
  ancienne_supprimee boolean;
begin
  select id into uid from auth.users limit 1;
  if uid is null then
    raise exception 'RESULTAT TEST ROTATION : aucun compte dans auth.users, test impossible (rien n''a été écrit).';
  end if;
  insert into public.backups (user_id, created_at, sessions_count, summary, fingerprint, payload)
  select uid,
         now() - (36 - g) * interval '1 minute',
         case when g = 3 then 2147483647 else 1000 + g end,
         '{"test": true}'::jsonb,
         '0000000' || (g % 10)::text,
         '{}'
  from generate_series(1, 35) as g;
  select count(*),
         count(*) filter (where summary ? 'test'),
         coalesce(bool_or(sessions_count = 2147483647 and summary ? 'test'), false),
         coalesce(bool_or(sessions_count = 1035 and summary ? 'test'), false),
         not coalesce(bool_or(sessions_count = 1001 and summary ? 'test'), false)
    into restantes, de_test, complete_gardee, recente_gardee, ancienne_supprimee
  from public.backups where user_id = uid;
  raise exception 'RESULTAT TEST ROTATION (annulé, aucune trace) : lignes_restantes=%, lignes_de_test_restantes=%, plus_complete_gardee=%, plus_recente_gardee=%, plus_ancienne_ordinaire_supprimee=%',
    restantes, de_test, complete_gardee, recente_gardee, ancienne_supprimee;
end $$;

-- 8. Après le test de rotation (attendu : même nombre de lignes qu'à la section 6,
--    lignes_de_test_restantes = 0)
select count(*) as lignes, count(*) filter (where summary ? 'test') as lignes_de_test_restantes
from public.backups;
