# Ovryk

Application de suivi de musculation et d'haltérophilie. Fichier unique index.html (HTML, CSS puis JavaScript, sans framework), données dans localStorage (clés ovryk.*), application installable (manifest.json, sw.js et icônes, qui sont dans le projet réel et pas dans ce dossier).

## À lire avant toute modification

1. dossier-lots/00-LIRE-EN-PREMIER.md puis dossier-lots/METHODE.md.
2. dossier-lots/ETAT-DES-LIEUX.md, MODELE-DE-DONNEES.md, REGLES-METIER.md, DECISIONS-A-PRENDRE.md, ECRANS-A-ADAPTER.md.
3. Le lot demandé : dossier-lots/lots/LOT-NN.md, et ses images dans dossier-lots/maquette/.

L'avancement se suit dans dossier-lots/PLAN.md. Les lots 00 à 07 sont faits, le lot 08 est le prochain. Ne jamais traiter plus d'un lot à la fois.

## Structure du projet

* index.html : l'application. Section "SKIN MAQUETTE" en fin de style pour le design.
* outils/ : verifier-cycles.js (contrôle des 12 cycles), extraire-cycles.js, generer-docs-cycles.js (écrit docs/CYCLES.md), exporter-cycles-json.js (écrit data/cycles_generiques.json).
* data/cycles_generiques.json et docs/CYCLES.md : fichiers générés depuis index.html. La source de vérité est FORCE_CYCLES dans index.html. Après toute modification des cycles, relancer les deux scripts de génération.
* docs/DESIGN.md : palette, polices, formes.
* sauvegarde/index.original.html : le fichier d'origine, avec les cycles A à E seulement. Ne jamais le modifier.
* dossier-lots/ : plan, règles et lots. dossier-lots/tests/smoke.py : test de fonctionnement.

## Règles

1. Un seul lot à la fois. Proposer un plan sans écrire de code, attendre la validation.
2. Ne jamais changer le format des clés ovryk.* sans migration idempotente testée avec un vrai export. Ne jamais supprimer ni renommer les identifiants 'A' à 'E' : des cycles en cours les utilisent. Seul le nom affiché change (A = Cycle 13, B = 14, C = 15, D = 16, E = 17).
3. Durée d'un cycle : toujours cycleLength(cycle.cycle_actif), jamais un 6 écrit en dur.
4. Aucune couleur en dur : variables de :root et section SKIN MAQUETTE. Orange = action principale et muscu, bleu = cycles et haltérophilie.
5. Textes affichés en français, sans emoji ni tiret long.
6. Les séances passées ne se réécrivent jamais : le 1RM est figé dans oneRepMaxSnapshot.
7. Après chaque étape : vérifier la syntaxe du script (extraire le script de index.html et lancer node --check), node outils/verifier-cycles.js, puis python dossier-lots/tests/smoke.py index.html.
8. Augmenter la version du cache dans sw.js à chaque livraison.
9. En cas de règle ambiguë : poser la question, ne pas choisir.

## Les 17 cycles

* 17 cycles au total : les 12 génériques ('1' à '12') et les anciens A à E, affichés Cycle 13 à Cycle 17 (6 semaines, test inclus en semaine 6). Tous entrent dans le tirage, sans répéter le cycle qui vient de finir. L'affichage 13 à 17, l'extension de verifier-cycles.js à 17 cycles et le tirage parmi les 17 sont à faire au lot 07 (Activation et tirage des cycles), pas avant : les lots 02 et 03 n'y touchent pas.

* Applicables à n'importe quel mouvement, clés '1' à '12' dans FORCE_CYCLES. Le tirage choisit le cycle, jamais le mouvement.
* 8 semaines, test 1RM en semaine 8 : cycles 1, 2, 6, 7. 7 semaines, test 1RM séparé en semaine 7 : cycles 3, 4, 5, 8, 9, 10, 11. 6 semaines, test inclus : cycle 12.
* Les vagues du type 3-2-1 sont lues comme 3 reps, 2 reps puis 1 rep.
