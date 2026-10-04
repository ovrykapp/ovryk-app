# LOT 11. Séparateur de bloc

Taille : S. Dépend de : 05, 09.

## Écrans de la maquette

* ../maquette/13-separateur-de-bloc.png

## Objectif

Afficher un écran de transition quand la séance passe du bloc cycle (haltérophilie) au bloc muscu.

## Existant à connaître

* L'ordre des exercices d'une séance suit la routine (rex.order). Rien ne distingue les blocs.

## À faire

1. Calculer sex.block à la construction de la séance : 'cycle' si l'exercice est piloté par un cycle ou un mode de base, sinon 'muscu'.
2. Quand le dernier exercice 'cycle' se termine et qu'un exercice 'muscu' suit, afficher l'écran de transition (maquette 13) : progression par bloc (haltérophilie terminé, muscu à venir), récapitulatif du bloc terminé (charges et résultats), séparateur "Bloc muscu", "Ce qui change" (double progression, reps comptées, repos), exercices à venir avec leurs charges, pause conseillée de 3 minutes avec "Passer", bouton "Commencer le bloc muscu".
3. La pause est une suggestion : elle ne bloque jamais le bouton.
4. Si l'ordre de la routine mélange les blocs, afficher le séparateur à chaque changement de bloc.

## Données

sex.block.

## Règles métier concernées

R6, R5, R10.

## Critères d'acceptation

* Une séance avec trois exercices de cycle puis deux de muscu affiche le séparateur une fois.
* Le récapitulatif donne les bonnes charges et les bons résultats.
* Une séance sans muscu, ou sans cycle, n'affiche pas de séparateur.

## Risques

* Séances reprises après interruption : ne pas réafficher un séparateur déjà passé.

## Hors lot

L'ordre automatique des blocs.

## Prompt pour Claude Code

Copie ce texte dans Claude Code, à la racine du projet, après avoir exporté tes données et fait un commit :

> Lis CLAUDE.md et les documents du dossier dossier-lots : METHODE.md, ETAT-DES-LIEUX.md, MODELE-DE-DONNEES.md, REGLES-METIER.md, puis lots/LOT-11.md et les images de maquette citées. Travaille uniquement sur le lot 11. Commence par me proposer un plan des modifications, sans écrire de code, en citant les fonctions et les identifiants que tu comptes toucher. Attends ma validation. Ensuite modifie index.html par petites étapes, vérifie la syntaxe du script, lance node outils/verifier-cycles.js, teste dans un navigateur à 390 x 844 et passe les critères d'acceptation un par un. Ne touche à rien d'autre. Si une règle est ambiguë, pose moi la question.
