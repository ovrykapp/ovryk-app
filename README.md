# Ovryk, projet complet

Ce dossier réunit l'application, les outils de vérification, les 12 cycles et le dossier des lots à construire.

## Contenu

* index.html : l'application, avec le lot 00 fait (12 cycles génériques, durée dynamique, style de la maquette).
* CLAUDE.md : consignes pour Claude Code.
* outils/ : scripts de vérification et de génération des cycles.
* data/cycles_generiques.json : les 12 cycles en JSON (fichier généré).
* docs/CYCLES.md : les 12 cycles semaine par semaine (fichier généré). docs/DESIGN.md : design.
* sauvegarde/index.original.html : ton fichier d'origine, intact.
* dossier-lots/ : 17 lots, règles métier, modèle de données, carte des 30 écrans, images de la maquette, test de fonctionnement.

## Mise en place dans VS Code

1. Décompresse le zip, puis Fichier, Ouvrir le dossier, et choisis le dossier ovryk. VS Code n'ouvre pas un zip directement.
2. Avant tout, exporte tes données depuis ton application actuelle (Réglages, Exporter) et garde ce fichier.
3. Dans ton vrai projet, remplace index.html par celui ci. Ne touche pas à manifest.json, sw.js ni aux icônes : ils ne sont pas dans ce dossier. Ouvre sw.js, repère la version du cache et augmente la d'un cran, sinon l'application installée garde l'ancien index.html.
4. Pour tester dans le navigateur : extension Live Server (recommandée par VS Code), clic droit sur index.html puis Open with Live Server.
5. Copie outils/, data/, docs/ et dossier-lots/ ainsi que CLAUDE.md dans ton vrai projet, à côté de index.html.

## Vérifier que tout fonctionne

    node outils/verifier-cycles.js
    python dossier-lots/tests/smoke.py index.html

Le second demande une fois : pip install playwright, puis playwright install chromium.

## Régénérer les fichiers dérivés

    node outils/generer-docs-cycles.js
    node outils/exporter-cycles-json.js

## Pour construire la suite

Lis dossier-lots/00-LIRE-EN-PREMIER.md, puis donne à Claude Code un lot à la fois en commençant par dossier-lots/lots/LOT-01.md. Le prompt à copier est à la fin de chaque lot.
