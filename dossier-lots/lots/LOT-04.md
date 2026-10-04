# LOT 04. Séance de muscu et double progression

Taille : M. Dépend de : 01.

## Écrans de la maquette

* ../maquette/02-seance-muscu.png

## Objectif

Refaire l'écran de séance de muscu : objectif du jour, minuteur de repos, séries, effort ressenti, chargement de barre. Compléter la double progression.

## Existant à connaître

* Séance active : renderSeanceActiveView, buildLiveSessionExercise, buildLiveSessionSetRow (kg, reps, case à cocher, suppression).
* Minuteur : startRestTimer appelé à la validation d'une série.
* Calculateur de disques : buildPlateCalcPanel, computePlateLoad.
* Progression : applyRangeProgression et cloneSetsFromPastSex (+2,5 kg quand repsMax est atteint).
* Les séries de muscu ont repType 'range' avec repsMin, repsMax, repsActual. Le RPE existe (set.rpe) mais n'a pas d'interface visible.

## À faire

1. En-tête de séance : titre de l'exercice, "Exercice X sur N", chronomètre. Chaque exercice s'affiche seul, avec "Ensuite : prochain exercice" en bas.
2. Carte de repos : grand compte à rebours orange, boutons moins 15 s, plus 15 s et Passer.
3. Carte "Objectif du jour" : "9 reps à 35 kg" et "Plage 8 à 10 reps" avec la charge de la prochaine montée. L'objectif vient de la règle R5.
4. Tableau des séries : colonnes Série, Précédent, Kg, Reps. La ligne en cours est mise en valeur et pré remplie avec l'objectif. Validation par un bouton "Valider la série N" qui remplace la case à cocher.
5. Effort ressenti : cinq boutons de 6 à 10 qui écrivent set.rpe.
6. Carte de chargement : "Par côté" et dessin des disques, à partir de computePlateLoad.
7. Double progression R5 : compléter applyRangeProgression avec l'objectif de reps (champ targetReps), le pas progressionStep et l'option autoProgression par exercice. Ajouter l'avertissement RPE 10.
8. Avertissement discret quand la charge monte ("Charge en hausse").

## Données

set.targetReps, exercise.progressionStep, exercise.autoProgression, settings.defaultProgressionStep et defaultRepRange.

## Règles métier concernées

R5 (double progression), R10 (repos).

## Critères d'acceptation

* Deux séances de suite : si toutes les séries atteignent le haut de la plage, la charge monte du pas et les reps repartent au bas de la plage.
* Si une série n'atteint pas le haut de la plage, la charge reste et l'objectif de reps augmente de 1.
* Sous le bas de la plage, la charge ne baisse pas.
* Avec un RPE 10 et une plage atteinte, un avertissement s'affiche et la montée n'est pas bloquée.
* L'option autoProgression désactivée garde la charge.
* Les charges déjà enregistrées ne sont pas modifiées.

## Risques

* Ne pas casser la reprise d'une séance en cours (persistActiveSession).
* Les séries Lifting suivent les cycles, pas la double progression : ne pas leur appliquer R5.

## Hors lot

Les séries d'haltérophilie (lot 05) et le séparateur de bloc (lot 11).

## Prompt pour Claude Code

Copie ce texte dans Claude Code, à la racine du projet, après avoir exporté tes données et fait un commit :

> Lis CLAUDE.md et les documents du dossier dossier-lots : METHODE.md, ETAT-DES-LIEUX.md, MODELE-DE-DONNEES.md, REGLES-METIER.md, puis lots/LOT-04.md et les images de maquette citées. Travaille uniquement sur le lot 04. Commence par me proposer un plan des modifications, sans écrire de code, en citant les fonctions et les identifiants que tu comptes toucher. Attends ma validation. Ensuite modifie index.html par petites étapes, vérifie la syntaxe du script, lance node outils/verifier-cycles.js, teste dans un navigateur à 390 x 844 et passe les critères d'acceptation un par un. Ne touche à rien d'autre. Si une règle est ambiguë, pose moi la question.
