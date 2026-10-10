# LOT 12. Historique et détail d'une séance

Taille : M. Dépend de : 05.

## Écrans de la maquette

* ../maquette/14-historique.png
* ../maquette/15-detail-d-une-seance.png

## Objectif

Ajouter une liste globale des séances et un écran de détail.

## Existant à connaître

* Les séances sont dans OvrykDB.getSessions(). L'historique existe seulement par exercice (getExerciseSessionRecords, buildHistoryRow).
* startOfWeek, weekKeyOf, formatShortDate, formatFullDate, sessionVolume, formatDuration.

## À faire

1. Bouton "Historique" en haut de l'écran Progrès, qui ouvre une page plein écran.
2. Liste (maquette 14) : filtres Tout, Muscu et Haltérophilie, séances regroupées par semaine avec total de séances et volume, chaque ligne avec la date, le nom, les pastilles, la durée et le volume.
3. Détail (maquette 15) : durée, volume, nombre de records ou numéro de semaine du cycle, liste des exercices avec charges et résultats (réussites en haltérophilie, reps par série en muscu), RPE moyen, bouton "Refaire cette séance" qui démarre la même routine.
4. Records : un exercice est un record si sa charge dépasse toutes les précédentes (utiliser getBestRecordForExercise ou getExerciseSessionRecords). Ne pas utiliser le mot record pour une charge ordinaire.
5. Les séances sans les nouveaux champs (anciennes) s'affichent avec les anciens libellés.

## Données

Aucun nouveau champ.

## Règles métier concernées

R6 pour l'affichage des réussites.

## Critères d'acceptation

* La liste montre toutes les séances terminées, regroupées par semaine.
* Les filtres fonctionnent.
* Le détail d'une séance ancienne s'affiche sans erreur.
* "Refaire cette séance" démarre la bonne routine.

## Risques

* Volume de données : prévoir un affichage par pages si le nombre de séances est élevé.

## Hors lot

Comparer deux séances entre elles.

## Réalisé (2026-10-10)

Lot d'interface seule, lecture seule de OvrykDB.getSessions(). Aucun champ ajouté, renommé ni supprimé, aucune écriture à l'ouverture d'un écran (vérifié : le stockage est identique avant et après l'ouverture de l'historique et des 84 détails de la copie de test).

* Bouton "Historique" dans Progrès, à côté de "Objectifs hebdomadaires" (dans progression-groups-view, donc absent des sous-vues). Il ouvre history-page.
* Liste : séances terminées seulement (la séance en cours n'y figure pas), triées de la plus récente à la plus ancienne, regroupées par semaine civile ("Cette semaine", "Semaine du 28 septembre", avec l'année pour une autre année), total de séances et de volume par semaine. Filtres Tout, Muscu, Haltérophilie : une séance qui contient les deux types porte les deux pastilles et sort sous les deux filtres ; Haltéro = au moins un exercice Lifting. Les totaux de semaine suivent le filtre. Pagination par 30 séances ("Afficher plus"), les totaux restent ceux de toute la semaine.
* Détail (history-detail-page) : durée (durationSeconds, sinon calculée depuis startedAt et completedAt, sinon "-"), volume (même computeSetVolume que partout), tuile Cycle (S et cycleWeekUsed) quand la séance en a, sinon tuile Records. Quatre exercices puis "N exercices de plus, A, B..." et "Tout voir" / "Réduire". Haltérophilie : séries réussies sur séries faites (R6, une série sans result compte comme réussie). Muscu : reps de chaque série, repsActual quand il existe (getMuscuSetReps), "-" sinon ; "par haltère" pour le matériel Haltères (décision 3A du lot 17). RPE moyen seulement si au moins une série faite en porte un.
* Record : la charge maximale de l'exercice dans cette séance dépasse strictement toutes celles des séances terminées précédentes (au moins une avant, avec une charge). Même source que la fiche exercice (getExerciseSessionRecords avec completedOnly). Jamais pour une première fois.
* "Refaire cette séance" : launchRoutineSession (chemin existant, popup de semaine de test comprise), mêmes garde-fous que le panneau du jour : "Reprendre la séance" si la même routine est en cours, bouton désactivé avec "Une autre séance est déjà en cours." sinon. Absent, avec une note, si la routine n'existe plus ou si la séance était libre. La séance relancée suit la routine actuelle, pas les séries de la séance passée.
* Accès au détail d'un cycle (demande de Ruben, hors texte du lot) : lignes de mouvement à cycle de la carte de séance de l'Accueil, tuile "Prochain test 1RM", et lignes "Cycle N, semaine X sur Y" dans les cartes du panneau du jour (Programme et Accueil). Au retour, l'écran d'origine se rafraîchit. L'écran de séance en cours n'est pas touché.

Testé à 390 px (cadre) avec l'export de backups/ complété en mémoire du navigateur de séances fabriquées : très longue (25 exercices, nom très long), vide, ancienne (sans durée, completedAt, notes, rpe, repsActual), routine supprimée, séance libre, 70 séances d'une autre année (pagination), séance en cours présente dans les données.

Hors texte du lot, notés dans PLAN.md : écart possible entre reps affichées (repsActual) et volume (milieu de plage).

## Prompt pour Claude Code

Copie ce texte dans Claude Code, à la racine du projet, après avoir exporté tes données et fait un commit :

> Lis CLAUDE.md et les documents du dossier dossier-lots : METHODE.md, ETAT-DES-LIEUX.md, MODELE-DE-DONNEES.md, REGLES-METIER.md, puis lots/LOT-12.md et les images de maquette citées. Travaille uniquement sur le lot 12. Commence par me proposer un plan des modifications, sans écrire de code, en citant les fonctions et les identifiants que tu comptes toucher. Attends ma validation. Ensuite modifie index.html par petites étapes, vérifie la syntaxe du script, lance node outils/verifier-cycles.js, teste dans un navigateur à 390 x 844 et passe les critères d'acceptation un par un. Ne touche à rien d'autre. Si une règle est ambiguë, pose moi la question.
