# LOT 07. Activation et tirage des cycles

Taille : M. Dépend de : 06.

## Écrans de la maquette

* ../maquette/24-tirer-mes-cycles.png
* ../maquette/29-cycles-tires-au-sort.png
* ../maquette/25-detail-d-un-cycle.png
* ../maquette/22-configurer-l-exercice.png

## Objectif

Permettre d'activer des cycles pour plusieurs mouvements d'un coup : choisir les mouvements, saisir les 1RM, tirer un cycle pour chacun, relancer, consulter le détail. Lire d'abord ECRANS-A-ADAPTER.md.

## Existant à connaître

* Activation actuelle : par exercice, dans la liste de la bibliothèque (buildExerciseRow, openOneRepMaxEditor, bouton de cycle), qui appelle OvrykDB.activateForceCycle.
* Détail : cycle-detail-page (openCycleDetailPage) liste les semaines et les charges.
* Les mouvements Lifting sont les exercices de catégorie Lifting.
* Le tirage actuel (tirerProchainCycle ou équivalent) ne porte encore que sur les 12 cycles génériques. Les cycles A à E existent déjà dans FORCE_CYCLES et CYCLE_NAMES (lot 00) mais n'entrent pas encore dans le tirage, et sont affichés tels quels ("Cycle A", "Cycle B"...) partout où le code construit 'Cycle ' + cycle.cycle_actif (badge de cycle, cycle-detail-page, carte Cycles en cours du Programme, détail d'exercice, bannière d'alerte).
* outils/verifier-cycles.js ne contrôle aujourd'hui que les 12 cycles génériques (GENERIC_CYCLE_IDS), pas les cycles A à E.

## À faire

1. Écran "Activer des cycles" : liste des mouvements Lifting avec une case à cocher et un champ de 1RM (pré rempli depuis l'exercice, orange s'il manque). Un 1RM manquant empêche le tirage de ce mouvement.
2. Bouton "Tirer mes cycles" : pour chaque mouvement coché, tirer un cycle parmi les 17 (R4) — les 12 génériques et les cycles A à E, en excluant le cycle qui vient de se terminer sur ce mouvement. Écran de résultat : une carte par mouvement avec "Cycle N : nom" (N va de 1 à 17, un cycle A à E affiché 13 à 17 — voir R1 et point 9 ci-dessous), la durée, la ligne "S1 : séries x reps à pourcentage, soit X kg", et un bouton pour relancer le tirage de cette carte. Boutons "Tout relancer" et "Valider".
3. Valider appelle activateForceCycle pour chaque mouvement avec le cycle choisi (étendre la fonction pour accepter un cycle imposé, et pour tirer parmi les 17 cycles quand aucun n'est imposé). Les 1RM saisis sont enregistrés sur les exercices. Ne jamais renommer ni supprimer les identifiants internes 'A' à 'E' (règle 2 du CLAUDE.md) : seul l'affichage change.
4. Accès : bouton "Activer des cycles" sur l'écran Programme (carte Cycles en cours vide ou bouton secondaire), et depuis la bibliothèque.
5. Détail d'un cycle (maquette 25) : restyler cycle-detail-page. Un cycle par mouvement, avec les charges calculées. Mention des semaines allégées, du pic et du test.
6. Réglage d'une semaine (maquette 22) : sur une semaine du détail, permettre de modifier le pourcentage de chaque série. La modification se stocke sur le cycle de l'exercice (champ semaines_modifiees) sans changer FORCE_CYCLES.
7. Pas de familles de mouvements.
8. Deuxième séance de la semaine (R12) : quand un mouvement de cycle figure dans deux routines de la même semaine, la deuxième séance baisse les pourcentages de j2OffsetPoints. Afficher "Séance légère" dans la séance. À ne faire qu'une fois le reste du lot validé.
9. Affichage Cycle 13 à 17 : partout où l'interface affiche 'Cycle ' + cycle.cycle_actif (badge de cycle, cycle-detail-page, carte Cycles en cours du Programme, détail d'exercice, bannière d'alerte de test), un cycle A à E doit apparaître comme Cycle 13 à Cycle 17 (A = 13, B = 14, C = 15, D = 16, E = 17), jamais comme "Cycle A". Les identifiants internes 'A' à 'E' ne changent pas. Prévoir une seule fonction de correspondance (ex. displayCycleNumber(cycle_actif)) réutilisée partout plutôt que de dupliquer la table de correspondance.
10. Étendre outils/verifier-cycles.js (et extraire-cycles.js si besoin) pour contrôler aussi les cycles A à E, avec les mêmes vérifications que les 12 génériques (durée cohérente, test 1RM à la bonne semaine).

## Données

cycle.semaines_modifiees (nouveau) : { numéro de semaine: tableau de séries }.

## Règles métier concernées

R4 (tirage), R1, R2, R12 (deuxième séance).

## Critères d'acceptation

* Cocher quatre mouvements, saisir leurs 1RM, tirer : quatre cartes avec un cycle chacune.
* Relancer une carte change seulement ce cycle.
* Valider crée quatre cycles actifs, visibles dans la carte Cycles en cours.
* Un mouvement sans 1RM ne peut pas être tiré.
* Modifier un pourcentage dans le détail change les charges de cette semaine pour ce mouvement uniquement.
* Aucun cycle déjà en cours n'est écrasé sans confirmation.
* Le tirage peut sortir un cycle A à E aussi bien qu'un cycle 1 à 12 ; tiré plusieurs fois de suite sur un même mouvement, il ne répète jamais le cycle qui vient de se terminer, identifiant interne A-E compris.
* Un cycle A à E actif s'affiche partout comme "Cycle 13" à "Cycle 17", jamais comme "Cycle A" à "Cycle E".
* node outils/verifier-cycles.js contrôle les 17 cycles (12 génériques et 13 à 17) et les 17 passent.

## Risques

* Ne pas activer deux fois un mouvement qui a déjà un cycle actif : demander une confirmation de remplacement.
* Les cycles activés sans coordination commencent tous la même semaine jusqu'au lot 08.
* Ne pas oublier un endroit où 'Cycle ' + cycle.cycle_actif est encore affiché brut (point 9) : chercher toutes les occurrences avant de livrer, pas seulement l'écran de résultat du tirage.

## Hors lot

Le décalage de départ et la règle des 2 cycles lourds (lot 08).

## Prompt pour Claude Code

Copie ce texte dans Claude Code, à la racine du projet, après avoir exporté tes données et fait un commit :

> Lis CLAUDE.md et les documents du dossier dossier-lots : METHODE.md, ETAT-DES-LIEUX.md, MODELE-DE-DONNEES.md, REGLES-METIER.md, puis lots/LOT-07.md et les images de maquette citées. Travaille uniquement sur le lot 07. Commence par me proposer un plan des modifications, sans écrire de code, en citant les fonctions et les identifiants que tu comptes toucher. Attends ma validation. Ensuite modifie index.html par petites étapes, vérifie la syntaxe du script, lance node outils/verifier-cycles.js, teste dans un navigateur à 390 x 844 et passe les critères d'acceptation un par un. Ne touche à rien d'autre. Si une règle est ambiguë, pose moi la question.
