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
| 09 | Muscu libre : éditeur de routine | 20, 21, 23, 7, 9 | fait | 04 |
| 10 | Types d'exercice et fiche exercice | 12, 6 | fait | 09 |
| 11 | Séparateur de bloc | 13 | S | 05, 09 |
| 12 | Historique et détail d'une séance (plus deux accès au détail d'un cycle, depuis l'Accueil et le panneau du jour) | 14, 15 | fait | 05 |
| 13 | Charge de la semaine et décharge de la muscu | 28 | M | 08, 09 |
| 14 | Réglages et matériel (cadré le 2026-10-10, 5 livraisons, 3 décisions en attente dans LOT-14.md : arrondi et plus petit saut, repos par type, portée des réglages par défaut) | 16, 17 | M | 01 |
| 15 | Import de données | 19, 8 | M | 14 |
| 16 | Compte et sauvegarde en ligne | 18 | L | tous |
| 17 | Séance sur un seul écran : tous les exercices en cartes repliables, cercle de validation à droite de chaque série, chargement selon le matériel (cadré et validé le 2026-10-10, décisions 1A, 2A, 3A ; livraisons 1 à 4 faites, plus quatre corrections hors livraison : reps fixes lues par repsActual, copie propre d'une série ajoutée, série en cours visible au dessus de la barre de repos, rappel Meilleur sur séances terminées ; livraison 5 en attente de ta séance test avec le nouvel écran) | 2, 3 adaptées (un exercice à la fois dans la maquette), 10, 11 | L | 05, 09, 10 |

## Ordre conseillé

1. Lots 01 à 03 : la structure et l'accueil. Ce sont eux qui changent le plus l'impression générale. Fait.
2. Lots 04 et 05 : la séance. C'est le coeur de l'usage au quotidien. Fait.
3. Lots 06 à 08 : les cycles complets (test, fin de cycle, tirage, coordination). Fait.
4. Lots 09 et 10 : la muscu libre, les types et la fiche exercice. Fait.
5. Reste à faire, dans cet ordre (mis à jour le 2026-10-10) : lot 17 livraison 5 (test de 1RM, avis R12, supersets, séparateur, retrait de l'ancien écran, après ta séance test), puis lot 11 (séparateur de bloc, à réécrire pour la liste de cartes), lot 14 (réglages et matériel), lot 13 (charge de la semaine et décharge de la muscu), lot 15 (import de données), lot 16 (compte et sauvegarde en ligne, en dernier car il dépend de tous les autres). Le lot 12 est fait.

## Livraisons hors plan

* Livraison E (après le lot 07, hors périmètre initial) : popup de choix en semaine de test non encore faite (Faire le test, Repousser le test d'une semaine, Changer de cycle sans tester). Fait.
* Sélecteur de jours de l'éditeur de routine (après le lot 10, hors périmètre d'un lot) : les 7 pastilles sous "Jours" remplacées par un bouton pleine largeur ouvrant une feuille (case à cocher par jour, bouton "Valider") ; rien n'est écrit dans routine.weekdays avant validation, même champ et même format qu'avant. Fait le 2026-10-10.

## Bugs hors lot

* Corrigé le 2026-10-10 : l'activation d'un cycle au fil de l'eau (maybeAutoActivateForceCycle — déclenchée depuis le 1RM de l'onglet Exercices, la date de départ, et depuis la livraison 4 du lot 09 "Charges de départ") ne lançait jamais la coordination (R7) : decalage_semaines restait à 0, même si maxHeavyCyclesPerWeek cycles lourds étaient déjà actifs ailleurs. Seule la validation groupée de "Tirer mes cycles" (handleValidateCyclesDrawn) appelait coordinateAndApplyOffsets. maybeAutoActivateForceCycle appelle désormais coordinateAndApplyOffsets après chaque nouvelle activation, sauf si l'exercice a une date de départ saisie à la main (forceCycleStartDate), jamais écrasée par la coordination. Le message "Cycle X démarre..." (Charges de départ, et la fiche exercice du lot 10) reflète le décalage éventuel via buildCycleStartMessage.

* Noté le 2026-10-10 (lot 17), non corrigé : ensurePlateSet écrit le jeu de disques par défaut dans les réglages quand il manque, y compris depuis un affichage (ancienne carte de chargement, calculateur de disques). La nouvelle carte du lot 17 lit sans écrire (getPlateSetForDisplay). Sans risque pour les données (n'écrase rien d'existant), mais contraire à "aucune écriture à l'ouverture d'un écran".
* Corrigé le 2026-10-10 (lot 17) : le rappel "Meilleur" d'une carte d'haltérophilie lisait la séance en cours (5x85 kg devenu 3x90 kg dès une série validée). getBestRecordForExercise ne lit plus que les séances terminées (getExerciseSessionRecords reçoit un paramètre completedOnly, les deux autres appelants, détection de stagnation et fiche exercice, sont inchangés).

* Noté le 2026-10-10 (lot 17), non corrigé : le volume et l'historique d'une série muscu en plage (repType 'range') utilisent le milieu de la plage (repsMin + repsMax) / 2 et ignorent repsActual, même quand il existe (147 séries dans l'export du 2026-10-01). Corriger la lecture changerait le volume, les records et le 1RM estimé de tout l'historique : à décider (règle 9). Les séries à reps fixes lisent maintenant repsActual quand il existe, sinon set.reps (getMuscuSetReps), donc les séances d'avant se lisent comme avant.
* Noté le 2026-10-10 (lot 17), non corrigé : la carte "objectif du jour" d'une série muscu à reps fixes affiche "- reps" et "Plage - à - reps" (elle ne lit que repsMin et repsMax). Comportement d'avant le lot.
* Noté le 2026-10-10 (lot 17), non corrigé : cloneSetsFromPastSex recopie result, repResults, failRep, failCause et repsDone d'une séance passée pour un mouvement Lifting sans cycle. La série copiée est à faire, mais un raté ou un compteur de la séance d'avant peut rester sur une série validée réussie. Même famille que la copie "+ Ajouter une série", corrigée.

* Noté le 2026-10-10 (lot 12), non corrigé : le détail d'une séance affiche les reps réellement faites (repsActual quand il existe, par exemple "8 8 7 reps") alors que le volume et les records restent calculés sur le milieu de la plage pour les séries en plage (voir l'anomalie précédente). Un écart visible est possible entre les reps affichées et le volume affiché. Même décision à prendre que pour cette anomalie.
* Noté le 2026-10-10 (lot 12) : dans le détail d'une séance, une série en plage sans repsActual (2 séries dans l'export du 2026-10-01) s'affiche "-" à la place des reps.

## Réglages sans interface

* settings.restByType ({ technique: 150, force: 120, muscu: 90 }, lot 10, R10) : seul addExercisesToRoutine le lit pour l'instant (repos par défaut à l'ajout d'un exercice dans une routine). Pas d'écran de réglage dans ce lot — à exposer plus tard (lot 14, Réglages et matériel, est le candidat naturel).

## Idées non traitées

* Accès au détail d'un cycle (openCycleDetailPage) : fait pour "Tes N cycles" et Coordination (point E, 2026-10-09), puis pour l'Accueil (lignes de cycle de la carte de séance, tuile "Prochain test 1RM") et le panneau du jour (Programme et Accueil, buildProgrammeDayPanelCard) au lot 12 (2026-10-10). Reste à faire si souhaité : depuis la séance en cours (buildHalteroLiveBody n'a aucun lien vers la vue complète du cycle ; le lot 12 n'y touche pas).
* Retrait possible des flèches monter/descendre dans l'éditeur de routine, devenues redondantes depuis le glisser-déposer (lot 09, livraison 3). Noté le 2026-10-10, pas encore retiré : à confirmer avant de supprimer une fonction existante (règle 9).

* Exercice à un seul haltère (ex. "Rowing haltère unilatéral") : la carte de chargement affiche "2 haltères de X kg". Un drapeau unilatéral par exercice serait nécessaire (lot 17, décision 3A : weightKg reste le poids d'un haltère). Noté le 2026-10-10.

## Points de livraison utiles

* Après le lot 03 : l'application a l'allure de la maquette.
* Après le lot 05 : tu peux t'entraîner avec le nouveau mode haltérophilie.
* Après le lot 08 : le système de cycles est complet.
* Après le lot 14 : plus rien à régler dans le code.
