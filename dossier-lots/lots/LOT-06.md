# LOT 06. Test 1RM séparé et fin de cycle

Taille : M. Dépend de : 05.

## Écrans de la maquette

* ../maquette/26-test-1rm-separe.png
* ../maquette/27-fin-de-cycle.png

## Objectif

Remplacer la validation immédiate du 1RM par un vrai parcours : tentatives réussies ou ratées, nouveau 1RM proposé, puis écran de fin de cycle avec le prochain cycle tiré.

## Existant à connaître

* buildCycleTestForm affiche un champ "Nouveau 1RM testé". OvrykDB.submitNewOneRM enregistre le 1RM, tire le prochain cycle (tirerProchainCycle) et remet la semaine à 1.
* Les semaines de test (isTestWeek) ont une montée de charge prête dans FORCE_CYCLES.
* Après le lot 00, la semaine de test existe pour tous les cycles (semaine 8, 7 ou 6 selon le cycle).

## À faire

1. Séance de test : afficher la liste des tentatives (maquette 26) avec la charge, le résultat réussi ou raté, et "Ajouter une tentative". Les charges viennent de la montée prévue. Réutiliser la saisie de réussite du lot 05.
2. Calculer le nouveau 1RM : la charge de la meilleure tentative réussie, dans un champ modifiable. Boutons "Valider mon 1RM" et "Garder mon 1RM actuel".
3. Remplacer submitNewOneRM par un enregistrement en deux temps : (a) enregistrer le 1RM et clore le cycle dans historique_cycles ; (b) tirer le prochain cycle et le stocker dans prochain_cycle avec en_attente_de_validation vrai, sans démarrer.
4. Écran "Cycle terminé" (maquette 27) : séances faites sur prévues, taux de réussite, 1RM avant et après. Section "Prochain cycle" avec la carte du cycle tiré (nom, durée, semaine 1 calculée avec le nouveau 1RM). Boutons "Relancer" (nouveau tirage, jamais le cycle qui finit), "Garder ce cycle", et "Choisir moi même" (liste des 12 cycles). Bouton "Lancer ce cycle" qui démarre.
5. La coordination (lot 08) fixera plus tard le décalage de départ : en attendant, le départ est immédiat.
6. Mettre à jour le bandeau d'alerte : il mène au test, puis à l'écran de fin de cycle tant qu'un cycle attend sa validation.
7. Garder le 1RM figé dans les séances passées (oneRepMaxSnapshot).

## Données

historique_cycles, prochain_cycle, en_attente_de_validation (voir MODELE-DE-DONNEES.md).

## Règles métier concernées

R3 (test), R4 (tirage), R2.

## Critères d'acceptation

* Un test avec trois tentatives réussies et une ratée propose la charge de la meilleure réussie.
* Le 1RM peut être corrigé ou laissé tel quel.
* Après validation, l'écran de fin de cycle montre le bilan et un cycle différent de celui qui vient de finir.
* "Relancer" tire un autre cycle, "Choisir moi même" permet n'importe lequel des 12.
* Le cycle ne démarre qu'après "Lancer ce cycle".
* Les séances déjà enregistrées gardent leurs charges.
* Un cycle A à E en cours se termine avec le même parcours.

## Risques

* Un cycle en attente de validation ne doit pas bloquer l'accès aux autres séances.
* Tester la fermeture de l'application entre la validation du 1RM et le lancement du cycle : l'état d'attente doit survivre.

## Hors lot

Le choix de plusieurs mouvements à la fois (lot 07) et la coordination (lot 08).

## Prompt pour Claude Code

Copie ce texte dans Claude Code, à la racine du projet, après avoir exporté tes données et fait un commit :

> Lis CLAUDE.md et les documents du dossier dossier-lots : METHODE.md, ETAT-DES-LIEUX.md, MODELE-DE-DONNEES.md, REGLES-METIER.md, puis lots/LOT-06.md et les images de maquette citées. Travaille uniquement sur le lot 06. Commence par me proposer un plan des modifications, sans écrire de code, en citant les fonctions et les identifiants que tu comptes toucher. Attends ma validation. Ensuite modifie index.html par petites étapes, vérifie la syntaxe du script, lance node outils/verifier-cycles.js, teste dans un navigateur à 390 x 844 et passe les critères d'acceptation un par un. Ne touche à rien d'autre. Si une règle est ambiguë, pose moi la question.
