# LOT 09. Muscu libre : éditeur de routine

Taille : M. Dépend de : 04.

## Écrans de la maquette

* ../maquette/20-creer-un-programme.png
* ../maquette/21-editer-une-seance.png
* ../maquette/23-configurer-un-exercice-muscu.png
* ../maquette/07-nouveau-programme.png
* ../maquette/09-charges-de-depart.png

## Objectif

Restyler l'éditeur de routine selon la maquette et y ajouter les réglages d'un exercice de muscu : plage de reps, charge de départ, pas de montée, progression automatique, allègement.

## Existant à connaître

* Éditeur plein écran : openRoutineEditor, renderRoutineEditor, buildRoutineExerciseBlock, buildSetRow, buildSetsHeaderRow, applyRepTypeToAllSets, addExercisesToRoutine, picker d'exercices.
* Liste : renderRoutineList, buildRoutineRow.
* Les séries ont repType 'fixed' ou 'range'. Les mouvements Lifting n'ont pas de charge saisie : elle vient du cycle (buildForceCyclePrescriptionBody) ou du mode de base (buildBaseModePrescriptionBody).

## À faire

1. Écran "Nouvelle routine" (maquette 7) : choix entre créer une séance de muscu, activer des cycles (lot 07) et importer (lot 15). Le parcours "Créer de zéro" mène à l'éditeur.
2. Éditeur de routine (maquette 20, 21) : nom de la séance, jours de la semaine (lot 02), liste des exercices dans l'ordre avec poignée de déplacement, pastille MUSCU ou HALTÉRO, résumé, bouton "Ajouter un exercice", bouton "Enregistrer".
3. Réglage d'un exercice de muscu (maquette 23) : séries, plage de reps (bas et haut), charge de départ, pas de montée (1, 2 ou 2,5), progression automatique, allègement en semaine allégée. Écrit set.repsMin et repsMax, set.weightKg, exercise.progressionStep, exercise.autoProgression, exercise.deloadMuscu.
4. Écran "Charges de départ" (maquette 9) : à ne construire que pour les 1RM manquants des mouvements Lifting de la routine et pour la charge de départ des exercices de muscu sans historique. C'est une étape facultative à la fin de la création.
5. Les valeurs par défaut viennent de settings.defaultProgressionStep et defaultRepRange (lot 14).

## Données

exercise.progressionStep, exercise.autoProgression, exercise.deloadMuscu, routine.weekdays.

## Règles métier concernées

R5, R8 pour l'option d'allègement.

## Critères d'acceptation

* Créer une routine de six exercices avec leurs plages de reps, la lier au lundi, la démarrer.
* Un exercice avec progression automatique se met à jour selon R5 à la séance suivante.
* Les routines existantes s'ouvrent et se modifient sans perte.
* Un mouvement Lifting dans la routine montre sa prescription de cycle, sans champ de charge.

## Risques

* L'éditeur est un gros morceau de code. Procéder par sous écrans : liste, éditeur, réglage d'un exercice.
* Ne pas changer le format de rex.sets, seulement ajouter des champs.

## Hors lot

Les types d'exercice (lot 10) et l'import (lot 15).

## Prompt pour Claude Code

Copie ce texte dans Claude Code, à la racine du projet, après avoir exporté tes données et fait un commit :

> Lis CLAUDE.md et les documents du dossier dossier-lots : METHODE.md, ETAT-DES-LIEUX.md, MODELE-DE-DONNEES.md, REGLES-METIER.md, puis lots/LOT-09.md et les images de maquette citées. Travaille uniquement sur le lot 09. Commence par me proposer un plan des modifications, sans écrire de code, en citant les fonctions et les identifiants que tu comptes toucher. Attends ma validation. Ensuite modifie index.html par petites étapes, vérifie la syntaxe du script, lance node outils/verifier-cycles.js, teste dans un navigateur à 390 x 844 et passe les critères d'acceptation un par un. Ne touche à rien d'autre. Si une règle est ambiguë, pose moi la question.
