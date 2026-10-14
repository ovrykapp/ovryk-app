# Modèle de données : ajouts et migration

Tous les ajouts sont optionnels et ont une valeur par défaut : un export ancien doit continuer à s'importer sans erreur.

## Version de schéma

Ajouter une clé ovryk.meta avec { schemaVersion: 2 }. Écrire une fonction migrateSchema(), idempotente, appelée à l'initialisation, qui complète les champs manquants. Elle ne supprime jamais rien.

## Ajouts par entité

### Routine
* weekdays : tableau de nombres de 1 (lundi) à 7 (dimanche). Défaut : tableau vide. Utilisé par les lots 02 et 03.

### Exercice
* exerciseType : 'technique', 'force' ou 'muscu'. Défaut calculé : Lifting avec liftBaseMode 'oly' donne 'technique', Lifting avec liftBaseMode 'force' donne 'force', toute autre catégorie donne 'muscu'. Lot 10.
* progressionStep : pas de montée en kg pour la double progression. Défaut : valeur des réglages (2,5). Lot 04.
* autoProgression : booléen, défaut true. Lot 04.
* deloadMuscu : retiré du plan le 2026-10-10 (lot 13), jamais créé. Il n'y a pas d'interrupteur de décharge par exercice : la décharge se règle pour toute la muscu (settings.deloadMuscuMode).

### Série de séance
* result : 'ok', 'fail' ou null (haltérophilie). Lot 05.
* repResults : tableau de booléens, un par rep (true = réussie). Lot 05.
* repsDone : nombre de reps réussies pour le mode compteur. Lot 05.
* failRep : numéro de la rep ratée (1 à N) ou null. Lot 05.
* failCause : 'devant', 'derriere', 'reception', 'pas_tire', 'autre' ou null. Lot 05.
* note : texte libre. Lot 05.
* targetReps : nombre de reps visé par la double progression. Lot 04.

### Exercice de séance
* block : 'cycle' (mouvement piloté par un cycle) ou 'muscu'. Calculé à la construction de la séance. Lot 11.
* deload : booléen, true si l'exercice est allégé (R8). Absent sur un exercice non allégé et sur toute séance antérieure. Lot 13, livraison 3.
* deloadRemovedSets : séries retirées par l'allègement, intactes, pour "Ignorer" et pour que la séance suivante reparte du nombre de séries d'origine. Lot 13, livraison 3.
* deloadSource : { exerciseId, cycleId, weekNumber } du cycle allégé (mode auto) ou 'manual' (bouton "Alléger cette séance"). Lot 13, livraison 3.
* deloadIgnored : true après "Ignorer". Lot 13, livraison 3.

### Cycle de force
Garder les champs existants et ajouter :
* historique_cycles : tableau de { cycle, debut, fin, seances, seances_prevues, reussite_pct, one_rm_avant, one_rm_apres }. Lot 06.
* prochain_cycle : identifiant du cycle tiré en attente de validation, ou null. Lot 06.
* en_attente_de_validation : booléen. Lot 06.
* decalage_semaines : nombre de semaines avant le démarrage, résultat de la coordination. Lot 08. Il se traduit en forceCycleStartDate pour réutiliser le mécanisme existant.

### Réglages
Ajouter, avec les valeurs par défaut suivantes :
* defaultProgressionStep : 2.5
* defaultRepRange : { min: 8, max: 10 }
* restByType : { technique: 150, force: 120, muscu: 90 } en secondes
* barWeightKg : 20
* deloadMuscuMode : 'off', 'auto' ou 'manual' (lot 13, livraison 3, décision du 2026-10-10). Absent = 'off', y compris pour les données existantes : migrateSchema ne l'écrit pas. Remplace le booléen deloadMuscu, jamais créé. Affiché dans Réglages (libellés Aucune, Automatique, Manuelle) seulement s'il existe au moins un cycle d'haltérophilie actif ; sinon masqué, valeur enregistrée conservée, et aucun allègement n'a lieu. Fait en v123.
* chargeAlertesMasquees : { clé de semaine (weekKeyOf): [clés d'alerte 'zone|jour|jour'] }, alertes de chevauchement masquées par "Je garde" (lot 13, livraison 2). Absent = aucune alerte masquée. Écrit seulement au clic sur "Je garde".
* heavyThreshold : 85 (pourcentage à partir duquel une semaine est lourde)
* maxHeavyCyclesPerWeek : 2
* j2OffsetPoints : 10 (baisse de la deuxième séance de la semaine, R12)
* lastImportAt : null

## Migration d'un cycle déjà en cours

Les cycles 'A' à 'E' continuent de fonctionner : ils restent définis dans FORCE_CYCLES sous ces clés. Ne jamais renommer ou supprimer ces clés. Seul l'affichage change : Cycle 13 à Cycle 17 (A = 13, B = 14, C = 15, D = 16, E = 17). Ils font partie du tirage, qui porte sur 17 cycles.

## Test de migration

1. Importer un export fait avant le lot.
2. Vérifier que les routines, séances, exercices et cycles sont identiques.
3. Vérifier que les nouveaux champs ont leur valeur par défaut.
4. Exporter, réimporter, comparer : le résultat doit être identique.

## Sauvegarde en ligne (lot 16, prévu, rien n'est encore créé)

Proposition du plan du 2026-10-10 (LOT-16.md), à confirmer après les décisions de Ruben :

* ovryk.cloud (nouvelle clé, optionnelle) : { enabled, lastSuccess: { at, sessionsCount, snapshotId }, lastError: { at, reason } }. Absente = sauvegarde en ligne désactivée. Jamais exportée ni mise dans un instantané.
* ovryk.cloud.auth (faite en v129, optionnelle) : { access_token, refresh_token, expires_at, user { id, email }, savedAt }, jamais le mot de passe. Absente = déconnecté. Jamais exportée, jamais restaurée, jamais dans une copie ; effacée par "Se déconnecter", par un refus définitif du jeton de renouvellement et par "Réinitialiser l'app".
* Point de restauration local (fait en livraison 1, v124) : base IndexedDB ovryk-restore, magasin points, { id, savedAt, reason, summary, raw } où raw contient les six clés ovryk.* en valeurs brutes (null si absente). 5 copies au plus. Créée seulement à la première restauration, jamais à l'ouverture d'un écran.
* Format d'export et d'instantané (fait en livraison 1, v124) : celui de collectAllOvrykData (version 1), avec en plus data.meta (ovryk.meta) et un bloc summary (sessionsCompleted, sessionsTotal, inProgressIds, lastSessionAt, routines, exercises, cycles, schemaVersion, checksum). Reste lisible par l'import d'avant, qui ignore les champs inconnus.
* Côté service : une table d'instantanés (identifiant du compte, date, résumé en colonnes, contenu JSON complet), ajout et lecture seulement depuis l'app, règles d'accès par ligne.
* ovryk.restoreInProgress (fait en v125, optionnelle) : { pointId, startedAt, mode }, posée juste avant le remplacement d'une restauration et retirée juste avant le rechargement. Absente en temps normal. Si elle est présente au lancement, un bandeau propose de revenir à la copie pointId. Jamais exportée (hors DB_KEYS).
* ovryk.cloud.lastUpload (faite en v130, optionnelle) : { at, id, fingerprint, sessionsCompleted } du dernier envoi en ligne vérifié. Absente = aucun envoi depuis cet appareil. Jamais exportée, jamais restaurée ; gardée à la déconnexion, effacée par "Réinitialiser l'app".
* Table Supabase public.backups (lot 16, livraison 3, dossier-lots/supabase/backups.sql) : id uuid, user_id (auth.uid()), created_at, schema_version, sessions_count, summary jsonb, fingerprint (^[0-9a-f]{8}$), payload texte (fichier d'export complet, 2 Mo au plus). RLS : lecture et ajout de ses propres lignes seulement ; rotation à 30 plus la plus complète.
