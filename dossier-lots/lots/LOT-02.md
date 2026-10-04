# LOT 02. Programme : cycles en cours et semaine

Taille : M. Dépend de : 01.

## Écrans de la maquette

* ../maquette/04-programme.png

## Objectif

Refaire l'écran Programme : la carte des cycles en cours, la liste des jours de la semaine avec leurs séances, et le bandeau d'alerte. Ajouter le jour de la semaine sur les routines.

## Existant à connaître

* Section view-routine : liste des routines (renderRoutineList, buildRoutineRow) et bouton + Nouvelle routine.
* La liste des cycles en cours est aujourd'hui sur l'accueil : renderDashboardForceCycles (#dash-force-cycles). Elle utilise cycleLength, getCycleWeek et openCycleDetailPage.
* Les routines n'ont pas de jour de la semaine.

## À faire

1. Ajouter le champ routine.weekdays (voir MODELE-DE-DONNEES.md) et l'initialiser à [] dans migrateSchema.
2. Dans l'éditeur de routine (openRoutineEditor, renderRoutineEditor), ajouter une rangée de 7 pastilles Lun à Dim, sélection multiple, qui écrit routine.weekdays. Mise à jour de updatedAt à l'enregistrement.
3. Écran Programme, de haut en bas : titre et sous titre "Semaine du lundi XX" ; carte "Cycles en cours" ; liste de la semaine ; bandeau "À surveiller" ; bouton + pour créer.
4. Carte "Cycles en cours" : une ligne par cycle actif avec nom du mouvement, "Semaine X sur N, phase" et une barre de progression à N segments (réutiliser la logique de renderDashboardForceCycles). Toucher une ligne ouvre cycle-detail-page. Retirer cette liste de l'accueil au lot 03, pas ici.
5. Liste de la semaine : sept lignes du lundi au dimanche. Pour chaque jour, les routines dont weekdays contient ce jour, avec le nom, le nombre d'exercices, une pastille HALTÉRO si la routine contient un mouvement piloté par un cycle (exercice Lifting avec cycle actif) et une pastille MUSCU pour le reste. Un jour sans routine affiche "Repos". Le jour d'aujourd'hui est surligné en orange. Une séance terminée ce jour là affiche une coche bleue.
6. Bandeau "À surveiller" : masqué tant que le lot 13 n'est pas livré.
7. Le bouton + ouvre la création de routine existante.

## Données

routine.weekdays (nouveau).

## Règles métier concernées

Aucune règle nouvelle. Les pastilles reprennent la distinction cycle ou muscu de R1.

## Critères d'acceptation

* Une routine peut être rattachée à un ou plusieurs jours.
* La semaine affiche les routines au bon jour, avec les bonnes pastilles.
* Le jour courant est surligné, un jour avec séance terminée porte une coche.
* La carte des cycles affiche chaque cycle actif avec sa durée réelle (6, 7 ou 8 semaines).
* Toucher un cycle ouvre son détail.
* Un export ancien s'importe sans routine.weekdays et l'écran fonctionne.

## Risques

* La détection d'un mouvement piloté par un cycle doit utiliser OvrykDB.getForceCycle(exerciseId).
* Une routine sans jour ne doit pas disparaître : prévoir une section "Sans jour" sous la semaine.

## Hors lot

L'alerte "À surveiller" (lot 13), la liste de l'accueil (lot 03).

## Prompt pour Claude Code

Copie ce texte dans Claude Code, à la racine du projet, après avoir exporté tes données et fait un commit :

> Lis CLAUDE.md et les documents du dossier dossier-lots : METHODE.md, ETAT-DES-LIEUX.md, MODELE-DE-DONNEES.md, REGLES-METIER.md, puis lots/LOT-02.md et les images de maquette citées. Travaille uniquement sur le lot 02. Commence par me proposer un plan des modifications, sans écrire de code, en citant les fonctions et les identifiants que tu comptes toucher. Attends ma validation. Ensuite modifie index.html par petites étapes, vérifie la syntaxe du script, lance node outils/verifier-cycles.js, teste dans un navigateur à 390 x 844 et passe les critères d'acceptation un par un. Ne touche à rien d'autre. Si une règle est ambiguë, pose moi la question.
