# LOT 11. Séparateur de bloc

Taille : S. Dépend de : 05, 09, 17. Statut : fait le 2026-10-10 (sw v116).

## Écrans de la maquette

* ../maquette/13-separateur-de-bloc.png

## Objectif

Marquer, dans la liste de séance du lot 17, le passage du bloc cycle (haltérophilie) au bloc muscu. Réécrit le 2026-10-10 après le lot 17 : l'écran de transition plein écran de la première version n'a plus de sens dans une liste où tous les exercices sont visibles. Le séparateur devient un élément de la liste, entre deux cartes.

## Existant à connaître

* L'ordre des exercices d'une séance suit la routine (rex.order). Rien ne distingue les blocs dans les données.
* Lot 17, livraison 5 : renderSeanceActiveView appelle buildLiveBlockSeparator(précédent, suivant) entre deux exercices consécutifs (ou entre un exercice et un superset). Le bloc est lu par getLiveExerciseBlock(sex) : 'cycle' si sex.cycleIdUsed ou catégorie Lifting, sinon 'muscu'. La fonction ne renvoie rien aujourd'hui : c'est l'emplacement à remplir.
* Les cartes repliées montrent déjà le résumé de chaque exercice (summarizeLiveExercise), terminé ou non.

## À faire

1. Remplir buildLiveBlockSeparator : quand le bloc change, renvoyer un élément de liste (pas un écran) avec la maquette 13 adaptée : "Bloc haltérophilie terminé" ou "en cours", récapitulatif du bloc qui précède (charges et résultats, lus sur les séries faites), "Bloc muscu", "Ce qui change" (double progression, reps comptées, repos), pause conseillée de 3 minutes avec "Passer".
2. La pause est une suggestion : elle ne bloque rien, aucune carte n'est verrouillée.
3. Si l'ordre de la routine mélange les blocs, un séparateur à chaque changement de bloc.
4. Le séparateur se recalcule à chaque rendu : rien à mémoriser, rien à écrire.

## Données

Aucune. Le champ sex.block prévu par la première version n'est plus nécessaire : le bloc se lit sur les champs déjà posés (getLiveExerciseBlock). L'état de la pause, s'il en faut un, reste en mémoire.

## Règles métier concernées

R6, R5, R10.

## Critères d'acceptation

* Une séance avec trois exercices de cycle puis deux de muscu montre un séparateur, entre la troisième et la quatrième carte.
* Le récapitulatif donne les bonnes charges et les bons résultats, et suit les validations et dé-validations.
* Une séance sans muscu, ou sans cycle, n'en montre aucun.
* Une séance reprise après rechargement montre le même séparateur au même endroit, sans écriture.

## Risques

* Le risque de la première version ("ne pas réafficher un séparateur déjà passé") disparaît : le séparateur est un élément fixe de la liste.
* Superset qui mélange un mouvement de cycle et un exercice de muscu : le séparateur ne doit pas couper le cadre du superset (renderSeanceActiveView appelle déjà la fonction seulement entre deux segments).

## Hors lot

L'ordre automatique des blocs.

## Prompt pour Claude Code

Copie ce texte dans Claude Code, à la racine du projet, après avoir exporté tes données et fait un commit :

> Lis CLAUDE.md et les documents du dossier dossier-lots : METHODE.md, ETAT-DES-LIEUX.md, MODELE-DE-DONNEES.md, REGLES-METIER.md, puis lots/LOT-11.md et les images de maquette citées. Travaille uniquement sur le lot 11. Commence par me proposer un plan des modifications, sans écrire de code, en citant les fonctions et les identifiants que tu comptes toucher. Attends ma validation. Ensuite modifie index.html par petites étapes, vérifie la syntaxe du script, lance node outils/verifier-cycles.js, teste dans un navigateur à 390 x 844 et passe les critères d'acceptation un par un. Ne touche à rien d'autre. Si une règle est ambiguë, pose moi la question.

## Réalisé

* buildLiveBlockSeparator rend, entre deux segments de la liste dont le bloc change : récapitulatif du bloc qui précède (bleu pour l'haltérophilie, orange pour la muscu), titre du bloc suivant, "Ce qui change" (charge, validation, repos du premier exercice du bloc suivant), pause conseillée de 3 min avec un bouton Lancer qui démarre la barre de repos (elle a son propre Passer). Le bouton "Commencer le bloc" de la maquette n'existe pas : les cartes ne sont pas verrouillées.
* Testé sur l'export de backups/ à 390 px : cycle puis muscu (1 séparateur), muscu seule (0), haltérophilie seule (0), cycle puis superset puis muscu (1, avant le groupe, aucun dedans), muscu puis superset (0), un seul exercice (0), muscu puis cycle (1), reprise après rechargement (même séparateur, sessions inchangées).
