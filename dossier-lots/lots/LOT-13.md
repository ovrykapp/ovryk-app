# LOT 13. Charge de la semaine et décharge de la muscu

Taille : M. Dépend de : 08, 09.

## Écrans de la maquette

* ../maquette/28-charge-de-la-semaine.png

## Objectif

Afficher la charge de la semaine (par jour, par groupe musculaire), avertir quand deux séances sollicitent la même zone, et alléger la muscu pendant les semaines allégées des cycles.

## Existant à connaître

* computeWeeklySeriesCounts (séries terminées par groupe et par semaine), PROGRESSION_GROUPS, DEFAULT_TARGETS, ensureMuscleGroupTargets, getProgressionGroup, JAMBES_GROUP_MAP.
* Les semaines allégées sont seulement visibles dans le nom de la phase ("Allégée ...").

## À faire

1. Ajouter un drapeau deload aux semaines de cycle : dans mkWeek, option deload ; l'activer sur toutes les semaines dont la phase commence par "Allégée" (cycles 2 à 12).
2. Écran "Charge de la semaine" (maquette 28) : bandeau "À surveiller" si un chevauchement existe (R9), histogramme des séries par jour (haltérophilie en bleu, muscu en orange), barres de séries par groupe musculaire avec l'étiquette "Élevé" au dessus de 1,3 fois l'objectif hebdomadaire.
3. Table des zones sollicitées par exercice, par exemple bas du dos : soulevés de terre, rowing barre, extensions lombaires, tirages et épaulés lourds. Une table dans le code, modifiable.
4. Alerte de chevauchement : R9. Boutons "Déplacer une séance" (change le jour de la routine, lot 02) et "Je garde" (masque l'alerte cette semaine).
5. Branchement : l'alerte alimente le bandeau "À surveiller" de l'écran Programme (lot 02).
6. Décharge de la muscu (R8) : à la construction d'une séance (buildSessionFromRoutine), si le réglage est actif et si au moins un cycle actif est en semaine allégée, retirer un tiers des séries de muscu (minimum 2). Marquer sex.deload et afficher "Séance allégée" avec un bouton "Ignorer".
7. Interrupteur "Alléger aussi la muscu" dans les réglages (lot 14) et par exercice (lot 09).

## Données

week.deload dans FORCE_CYCLES, sex.deload, settings.deloadMuscu.

## Règles métier concernées

R8, R9.

## Critères d'acceptation

* En semaine allégée d'un cycle, une routine de muscu de six exercices à trois séries ne propose plus que deux séries par exercice.
* "Ignorer" restaure les séries d'origine.
* Un chevauchement de bas du dos mardi et jeudi déclenche l'alerte, pas lundi et jeudi.
* Les barres par groupe correspondent à computeWeeklySeriesCounts.

## Risques

* Le seuil de 1,3 fois l'objectif et la table des zones sont des repères à ajuster à l'usage.
* L'allègement ne doit jamais supprimer une série déjà validée.

## Hors lot

Un coefficient de fatigue différent par mouvement.

## Prompt pour Claude Code

Copie ce texte dans Claude Code, à la racine du projet, après avoir exporté tes données et fait un commit :

> Lis CLAUDE.md et les documents du dossier dossier-lots : METHODE.md, ETAT-DES-LIEUX.md, MODELE-DE-DONNEES.md, REGLES-METIER.md, puis lots/LOT-13.md et les images de maquette citées. Travaille uniquement sur le lot 13. Commence par me proposer un plan des modifications, sans écrire de code, en citant les fonctions et les identifiants que tu comptes toucher. Attends ma validation. Ensuite modifie index.html par petites étapes, vérifie la syntaxe du script, lance node outils/verifier-cycles.js, teste dans un navigateur à 390 x 844 et passe les critères d'acceptation un par un. Ne touche à rien d'autre. Si une règle est ambiguë, pose moi la question.
