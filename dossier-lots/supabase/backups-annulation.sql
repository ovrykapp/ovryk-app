-- Ovryk, lot 16, livraison 3 : annulation de backups.sql.
-- ATTENTION : supprime la table ET toutes les sauvegardes en ligne. Irréversible.
-- Les données de l'app sur le téléphone ne sont pas touchées.

drop trigger if exists backups_rotate_after_insert on public.backups;
drop function if exists public.backups_rotate();
drop table if exists public.backups;

notify pgrst, 'reload schema';
