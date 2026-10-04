# LOT 15. Import de données

Taille : M. Dépend de : 14.

## Écrans de la maquette

* ../maquette/19-importer-mes-donnees.png
* ../maquette/08-verifier-l-import.png

## Objectif

Importer des séances depuis un fichier CSV d'une autre application ou depuis une sauvegarde Ovryk, avec un écran de vérification.

## Existant à connaître

* L'import d'une sauvegarde Ovryk existe (bouton Importer, JSON). Rien pour les CSV.

## À faire

1. Écran "Importer mes données" (maquette 19) : choix de la source (Hevy en CSV, Strong en CSV, sauvegarde Ovryk, autre CSV), choix du fichier.
2. Lecture du CSV : détecter les colonnes, regrouper en séances (une séance par date et par nom), séries avec charge et reps.
3. Écran de vérification (maquette 8, adapté) : résumé (nombre de séances, d'exercices, de mois), exercices non reconnus à associer à la bibliothèque ou à créer, choix "Ajouter à mon historique" (doublons ignorés) ou "Remplacer mon historique" avec confirmation.
4. Détection des doublons : même date, même exercice, mêmes séries.
5. Mise à jour de lastImportAt.
6. Faire une sauvegarde automatique (export téléchargé) avant tout remplacement.

## Données

settings.lastImportAt, sessions importées avec importedFrom.

## Règles métier concernées

Aucune.

## Critères d'acceptation

* Un CSV exporté depuis chacune des deux applications s'importe, avec les exercices non reconnus à associer.
* Importer deux fois le même fichier ne crée pas de doublons.
* "Remplacer" demande une confirmation et déclenche une sauvegarde avant.
* Les séances importées apparaissent dans l'historique (lot 12).

## Risques

* Les formats d'export des applications tierces changent : prévoir une lecture tolérante et un message clair si une colonne manque.
* Ne jamais promettre l'import d'un programme par photo ou PDF (décision 8).

## Hors lot

Import d'un programme depuis une photo ou un PDF.

## Prompt pour Claude Code

Copie ce texte dans Claude Code, à la racine du projet, après avoir exporté tes données et fait un commit :

> Lis CLAUDE.md et les documents du dossier dossier-lots : METHODE.md, ETAT-DES-LIEUX.md, MODELE-DE-DONNEES.md, REGLES-METIER.md, puis lots/LOT-15.md et les images de maquette citées. Travaille uniquement sur le lot 15. Commence par me proposer un plan des modifications, sans écrire de code, en citant les fonctions et les identifiants que tu comptes toucher. Attends ma validation. Ensuite modifie index.html par petites étapes, vérifie la syntaxe du script, lance node outils/verifier-cycles.js, teste dans un navigateur à 390 x 844 et passe les critères d'acceptation un par un. Ne touche à rien d'autre. Si une règle est ambiguë, pose moi la question.
