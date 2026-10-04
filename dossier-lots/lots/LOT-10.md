# LOT 10. Types d'exercice et fiche exercice

Taille : M. Dépend de : 09.

## Écrans de la maquette

* ../maquette/12-type-d-exercice.png
* ../maquette/06-fiche-exercice.png

## Objectif

Introduire les trois types d'exercice (technique, force, muscu) et refaire la fiche d'un exercice, sans vidéo.

## Existant à connaître

* liftBaseMode ('oly' ou 'force') sur les exercices Lifting, migrateExerciseCatalog, OLY_LIFT_NAMES. Les autres catégories n'ont pas de type.
* La fiche actuelle est l'écran de détail d'un exercice de Progrès : openExerciseDetail (graphiques, historique, meilleur record).

## À faire

1. Ajouter exercise.exerciseType avec le calcul par défaut de MODELE-DE-DONNEES.md.
2. Écran "Type d'exercice" (maquette 12) : trois cartes (mouvement technique, force en pourcentage, accessoire et muscu) avec charge, validation et repos, et le résultat calculé pour la prescription en cours.
3. Le type pilote : le mode d'affichage de la séance (lots 04 et 05), le repos par défaut (restByType, R10) et la progression (R5 pour la muscu, cycle ou pourcentage sinon).
4. Fiche exercice (maquette 6) : nom, type avec lien vers l'écran de type, meilleur record, 1RM, cycle actif, historique. La partie "phases du mouvement" est facultative : à ne faire que si tu rédiges les contenus. Pas de vidéo.
5. Accès à la fiche depuis l'onglet Exercices et depuis Progrès.

## Données

exercise.exerciseType.

## Règles métier concernées

R10 (repos par type), R5, R6.

## Critères d'acceptation

* Chaque exercice a un type, modifiable.
* Changer le type d'un exercice change son mode de séance et son repos par défaut.
* La fiche affiche les bonnes informations pour un mouvement Lifting et pour un exercice de muscu.

## Risques

* Un exercice dont le type change pendant une séance en cours : appliquer au démarrage de la prochaine séance seulement.

## Hors lot

Le contenu pédagogique des phases d'un mouvement.

## Prompt pour Claude Code

Copie ce texte dans Claude Code, à la racine du projet, après avoir exporté tes données et fait un commit :

> Lis CLAUDE.md et les documents du dossier dossier-lots : METHODE.md, ETAT-DES-LIEUX.md, MODELE-DE-DONNEES.md, REGLES-METIER.md, puis lots/LOT-10.md et les images de maquette citées. Travaille uniquement sur le lot 10. Commence par me proposer un plan des modifications, sans écrire de code, en citant les fonctions et les identifiants que tu comptes toucher. Attends ma validation. Ensuite modifie index.html par petites étapes, vérifie la syntaxe du script, lance node outils/verifier-cycles.js, teste dans un navigateur à 390 x 844 et passe les critères d'acceptation un par un. Ne touche à rien d'autre. Si une règle est ambiguë, pose moi la question.
