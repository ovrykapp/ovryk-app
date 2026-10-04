# Ovryk : dossier de lots

Ce dossier décrit tout ce qu'il reste à faire pour que l'application Ovryk ressemble à la maquette et fonctionne comme prévu. Le travail est découpé en 17 lots. Chaque lot se livre, se teste et se garde avant de passer au suivant.

## Contenu

* PLAN.md : l'ordre des lots, leurs dépendances et leur taille.
* METHODE.md : comment travailler un lot de bout en bout.
* ETAT-DES-LIEUX.md : ce qui existe déjà dans Ovryk, avec les noms de fonctions et d'éléments.
* MODELE-DE-DONNEES.md : les champs à ajouter et la migration.
* REGLES-METIER.md : toutes les règles (cycles, progression, tests, coordination, décharge).
* CARTE-DES-ECRANS.md : chaque écran de la maquette, son lot, sa cible dans Ovryk.
* ECRANS-A-ADAPTER.md : les écrans de la maquette qui contredisent le modèle actuel. À lire avant les lots 7, 8 et 6.
* DECISIONS-A-PRENDRE.md : les points qui demandent ton avis.
* lots/ : un document par lot.
* maquette/ : les 30 écrans en image.
* tests/ : jeu de données et test de fonctionnement.

## Ce qui est déjà fait (lot 00)

Les 12 cycles génériques, la durée dynamique des cycles, le test 1RM séparé en semaine 7 pour les cycles de 6 semaines, et le style de la maquette (couleurs, polices, navigation à plat). Cela se trouve dans le zip ovryk-maquette.

## Installation

1. Décompresse le zip : tu obtiens un dossier dossier-lots.
2. Pose dossier-lots à la racine de ton projet, à côté de index.html.
3. Copie dossier-lots/CLAUDE.md à la racine du projet. Si tu as déjà un CLAUDE.md (celui du zip ovryk-maquette), remplace le par celui ci.
4. Garde aussi le dossier outils du zip ovryk-maquette : les lots s'appuient sur node outils/verifier-cycles.js.
5. Ouvre le projet dans VS Code, puis dans Claude Code.

## Pour commencer

1. Lis METHODE.md.
2. Lis ECRANS-A-ADAPTER.md et DECISIONS-A-PRENDRE.md.
3. Ouvre lots/LOT-01 et donne son contenu à Claude Code, un lot à la fois.

Ne donne jamais plusieurs lots à la fois. Un fichier de 7 500 lignes se casse vite.
