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

## Prompt pour Claude Code

Copie ce texte dans Claude Code, à la racine du projet, après avoir exporté tes données et fait un commit :

> Lis CLAUDE.md et les documents du dossier dossier-lots : METHODE.md, ETAT-DES-LIEUX.md, MODELE-DE-DONNEES.md, REGLES-METIER.md, puis lots/LOT-12.md et les images de maquette citées. Travaille uniquement sur le lot 12. Commence par me proposer un plan des modifications, sans écrire de code, en citant les fonctions et les identifiants que tu comptes toucher. Attends ma validation. Ensuite modifie index.html par petites étapes, vérifie la syntaxe du script, lance node outils/verifier-cycles.js, teste dans un navigateur à 390 x 844 et passe les critères d'acceptation un par un. Ne touche à rien d'autre. Si une règle est ambiguë, pose moi la question.
