# Plan des lots

Taille : S = moins d'une heure de travail assisté, M = une demi journée, L = une journée ou plus.

| Lot | Titre | Écrans de la maquette | Taille | Dépend de |
|---|---|---|---|---|
| 00 | Socle : 12 cycles, durée dynamique, style | aucun | fait | |
| 01 | Navigation et en-têtes | 1, 4, 5, 6, 16 (barre et titres) | fait | 00 |
| 02 | Programme : cycles en cours et semaine | 4 | fait | 01 |
| 03 | Accueil : séance du jour | 1 | fait | 02 |
| 04 | Séance de muscu et double progression | 2 | fait | 01 |
| 05 | Séance d'haltérophilie : réussi ou raté | 3, 10, 11 | fait | 04 |
| 06 | Test 1RM séparé et fin de cycle | 26, 27 | fait | 05 |
| 07 | Activation et tirage des cycles (inclut l'affichage Cycle 13-17 et verifier-cycles.js étendu à 17) | 24, 29, 25, 22 | fait | 06 |
| 08 | Coordination des cycles | 30 | fait | 07 |
| 09 | Muscu libre : éditeur de routine | 20, 21, 23, 7, 9 | M | 04 |
| 10 | Types d'exercice et fiche exercice | 12, 6 | M | 09 |
| 11 | Séparateur de bloc | 13 | S | 05, 09 |
| 12 | Historique et détail d'une séance | 14, 15 | M | 05 |
| 13 | Charge de la semaine et décharge de la muscu | 28 | M | 08, 09 |
| 14 | Réglages et matériel | 16, 17 | M | 01 |
| 15 | Import de données | 19, 8 | M | 14 |
| 16 | Compte et sauvegarde en ligne | 18 | L | tous |
| 17 | À définir : séance sur un seul écran, cercle de validation par série | aucun (absent de la maquette 02/03, qui montre un exercice à la fois avec un bouton "Valider la série" plein largeur) | à définir | 05, 09 |

## Ordre conseillé

1. Lots 01 à 03 : la structure et l'accueil. Ce sont eux qui changent le plus l'impression générale.
2. Lots 04 et 05 : la séance. C'est le coeur de l'usage au quotidien.
3. Lots 06 à 08 : les cycles complets (test, fin de cycle, tirage, coordination).
4. Lots 09 à 13 : la muscu libre, les types, l'historique et les alertes.
5. Lots 14 à 16 : réglages, import, sauvegarde en ligne.

## Livraisons hors plan

* Livraison E (après le lot 07, hors périmètre initial) : popup de choix en semaine de test non encore faite (Faire le test, Repousser le test d'une semaine, Changer de cycle sans tester). Fait.

## Bugs hors lot

* L'activation d'un cycle au fil de l'eau (maybeAutoActivateForceCycle — déclenchée depuis le 1RM de l'onglet Exercices, et depuis la livraison 4 du lot 09 "Charges de départ") ne lance jamais la coordination (R7) : decalage_semaines reste à 0, même si maxHeavyCyclesPerWeek cycles lourds sont déjà actifs ailleurs. Seule la validation groupée de "Tirer mes cycles" (handleValidateCyclesDrawn) appelle coordinateAndApplyOffsets. Vérifié sur la copie locale le 2026-10-10 (livraison 4) : activer un 3ᵉ cycle avec Deadlift et Back Squat déjà actifs ne décale rien. Ne casse aucune donnée, pas de blocage.

## Idées non traitées

* Accès au détail d'un cycle (openCycleDetailPage) depuis l'Accueil (aucune carte "cycles en cours" n'y existe aujourd'hui), depuis le panneau du jour du calendrier (Programme/Accueil, buildProgrammeDayPanelCard ne montre que nom et nombre d'exercices), et depuis la séance en cours (buildHalteroLiveBody n'a aucun lien vers la vue complète du cycle). Fait pour "Tes N cycles" et Coordination (point E, 2026-10-09) ; ces trois-là restent à faire si souhaité.

## Points de livraison utiles

* Après le lot 03 : l'application a l'allure de la maquette.
* Après le lot 05 : tu peux t'entraîner avec le nouveau mode haltérophilie.
* Après le lot 08 : le système de cycles est complet.
* Après le lot 14 : plus rien à régler dans le code.
