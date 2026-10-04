# LOT 00. Socle (fait)

Livré dans le zip ovryk-maquette.

## Ce qui est fait

* 12 cycles génériques applicables à n'importe quel mouvement, définis dans FORCE_CYCLES sous les clés '1' à '12'. Détail dans docs/CYCLES.md du zip.
* Durée de cycle dynamique : cycleLength remplace tous les 6 écrits en dur (badge, détail, accueil, bandeau d'alerte, formulaire de test).
* Test 1RM : en semaine 8 pour les cycles de 8 semaines, en semaine 7 séparée pour les cycles de 6 semaines, en semaine 6 pour le cycle 12.
* Tirage du prochain cycle parmi les 12, sans répéter le cycle qui finit (tirerProchainCycle).
* Les cycles A à E restent définis pour les cycles déjà en cours.
* Style de la maquette : variables de couleur, polices Barlow et Barlow Condensed, navigation à plat avec bouton Séance orange, cycles en bleu, onglets renommés.

## À vérifier avant le lot 01

* node outils/verifier-cycles.js affiche "Tous les cycles sont valides".
* L'application s'ouvre sans erreur et affiche un cycle en cours avec sa durée réelle.
* Un export fait avant le zip s'importe encore.
