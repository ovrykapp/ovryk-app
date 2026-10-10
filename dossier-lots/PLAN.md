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
| 11 | Séparateur de bloc (élément de la liste de séance du lot 17, fait le 2026-10-10, sw v116 : buildLiveBlockSeparator) | 13 | Charge de la semaine et décharge de la muscu (plan validé le 2026-10-10, décisions : progression figée après une séance allégée, chevauchement à 2 jours calendaires ou moins, réglage settings.deloadMuscuMode à trois valeurs 'off', 'auto', 'manual', absent = 'off', affiché seulement avec un cycle d'haltérophilie actif ; interrupteur par exercice retiré. Livraison 1 faite (sw v118) : drapeau deload, grille de coordination, écran Charge de la semaine en lecture seule ; livraison 2 faite (sw v119) : Je garde, Déplacer une séance avec confirmation, bandeau À surveiller du Programme ; livraison 3 en attente : réglage à trois valeurs, bouton manuel, allègement) | 28 | M | 08, 09 |
| 12 | Historique et détail d'une séance (plus deux accès au détail d'un cycle, depuis l'Accueil et le panneau du jour) | 14, 15 | fait | 05 |
| 13 | Charge de la semaine et décharge de la muscu (plan détaillé écrit le 2026-10-10 dans LOT-13.md, en attente de validation : 4 livraisons, lecture seule, actions de l'alerte, réglage deloadMuscu avec allègement, interrupteur par exercice ; 3 décisions à prendre) | 28 | M | 08, 09 |
| 14 | Réglages et matériel (cadré le 2026-10-10, décisions 1A, 2A, 3A ; livraisons 1 Réglages restructuré et 3 Barre et disques faites ; livraisons 2 palier et plage par défaut, 4 plus petit saut appliqué à la progression, 5 repos par type en attente) | 16, 17 | M | 01 |
| 15 | Import de données | 19, 8 | M | 14 |
| 16 | Compte et sauvegarde en ligne | 18 | L | tous |
| 17 | Séance sur un seul écran : tous les exercices en cartes repliables, cercle de validation à droite de chaque série, chargement selon le matériel (cadré et validé le 2026-10-10, décisions 1A, 2A, 3A ; livraisons 1 à 4 faites, plus quatre corrections hors livraison : reps fixes lues par repsActual, copie propre d'une série ajoutée, série en cours visible au dessus de la barre de repos, rappel Meilleur sur séances terminées ; livraison 5 faite le 2026-10-10 après ta séance test : test de 1RM et avis R12 dans la carte, supersets encadrés, emplacement du séparateur, objectif à reps fixes, compteur bleu, retrait de l'ancien écran) | 2, 3 adaptées (un exercice à la fois dans la maquette), 10, 11 | fait | 05, 09, 10 |

## Ordre conseillé

1. Lots 01 à 03 : la structure et l'accueil. Ce sont eux qui changent le plus l'impression générale. Fait.
2. Lots 04 et 05 : la séance. C'est le coeur de l'usage au quotidien. Fait.
3. Lots 06 à 08 : les cycles complets (test, fin de cycle, tirage, coordination). Fait.
4. Lots 09 et 10 : la muscu libre, les types et la fiche exercice. Fait.
5. Reste à faire, dans cet ordre (mis à jour le 2026-10-10) : lot 14 livraisons 2 (palier et plage par défaut), 4 (plus petit saut appliqué à la progression) et 5 (repos par type), lot 13 livraison 3 (réglage deloadMuscuMode, bouton manuel et allègement ; livraisons 1 et 2 faites), lot 15 (import de données), lot 16 (compte et sauvegarde en ligne, en dernier car il dépend de tous les autres). Les lots 11, 12 et 17 sont faits, ainsi que l'édition directe des séries, kilos et reps dans l'éditeur de routine (v113 à v115, avec gardes : champ vidé et min supérieur au max refusés). À décider : le bouton Reps/Plage de l'en-tête de l'éditeur s'applique à toutes les séries et fait perdre la plage d'origine au retour à reps fixes.

## Livraisons hors plan

* Livraison E (après le lot 07, hors périmètre initial) : popup de choix en semaine de test non encore faite (Faire le test, Repousser le test d'une semaine, Changer de cycle sans tester). Fait.
* Sélecteur de jours de l'éditeur de routine (après le lot 10, hors périmètre d'un lot) : les 7 pastilles sous "Jours" remplacées par un bouton pleine largeur ouvrant une feuille (case à cocher par jour, bouton "Valider") ; rien n'est écrit dans routine.weekdays avant validation, même champ et même format qu'avant. Fait le 2026-10-10.

## Bugs hors lot

* Corrigé le 2026-10-10 : l'activation d'un cycle au fil de l'eau (maybeAutoActivateForceCycle — déclenchée depuis le 1RM de l'onglet Exercices, la date de départ, et depuis la livraison 4 du lot 09 "Charges de départ") ne lançait jamais la coordination (R7) : decalage_semaines restait à 0, même si maxHeavyCyclesPerWeek cycles lourds étaient déjà actifs ailleurs. Seule la validation groupée de "Tirer mes cycles" (handleValidateCyclesDrawn) appelait coordinateAndApplyOffsets. maybeAutoActivateForceCycle appelle désormais coordinateAndApplyOffsets après chaque nouvelle activation, sauf si l'exercice a une date de départ saisie à la main (forceCycleStartDate), jamais écrasée par la coordination. Le message "Cycle X démarre..." (Charges de départ, et la fiche exercice du lot 10) reflète le décalage éventuel via buildCycleStartMessage.

* Corrigé le 2026-10-10 (lot 14, livraison 3) : ensurePlateSet est supprimé, tous les affichages lisent getPlateSetForDisplay sans rien écrire. Ancienne note du lot 17 : ensurePlateSet écrit le jeu de disques par défaut dans les réglages quand il manque, y compris depuis un affichage (ancienne carte de chargement, calculateur de disques). La nouvelle carte du lot 17 lit sans écrire (getPlateSetForDisplay). Sans risque pour les données (n'écrase rien d'existant), mais contraire à "aucune écriture à l'ouverture d'un écran".
* Corrigé le 2026-10-10 (lot 17) : le rappel "Meilleur" d'une carte d'haltérophilie lisait la séance en cours (5x85 kg devenu 3x90 kg dès une série validée). getBestRecordForExercise ne lit plus que les séances terminées (getExerciseSessionRecords reçoit un paramètre completedOnly, les deux autres appelants, détection de stagnation et fiche exercice, sont inchangés).

* Noté le 2026-10-10 (lot 17), non corrigé : le volume et l'historique d'une série muscu en plage (repType 'range') utilisent le milieu de la plage (repsMin + repsMax) / 2 et ignorent repsActual, même quand il existe (147 séries dans l'export du 2026-10-01). Corriger la lecture changerait le volume, les records et le 1RM estimé de tout l'historique : à décider (règle 9). Les séries à reps fixes lisent maintenant repsActual quand il existe, sinon set.reps (getMuscuSetReps), donc les séances d'avant se lisent comme avant.
* Noté le 2026-10-10 (lot 17), non corrigé : la carte "objectif du jour" d'une série muscu à reps fixes affiche "- reps" et "Plage - à - reps" (elle ne lit que repsMin et repsMax). Comportement d'avant le lot.
* Corrigé le 2026-10-10 (voir la note plus bas) : cloneSetsFromPastSex recopie result, repResults, failRep, failCause et repsDone d'une séance passée pour un mouvement Lifting sans cycle. La série copiée est à faire, mais un raté ou un compteur de la séance d'avant peut rester sur une série validée réussie. Même famille que la copie "+ Ajouter une série", corrigée.

* Noté le 2026-10-10 (lot 12), non corrigé : le détail d'une séance affiche les reps réellement faites (repsActual quand il existe, par exemple "8 8 7 reps") alors que le volume et les records restent calculés sur le milieu de la plage pour les séries en plage (voir l'anomalie précédente). Un écart visible est possible entre les reps affichées et le volume affiché. Même décision à prendre que pour cette anomalie.
* Noté le 2026-10-10 (lot 12) : dans le détail d'une séance, une série en plage sans repsActual (2 séries dans l'export du 2026-10-01) s'affiche "-" à la place des reps.

* Corrigé le 2026-10-10 (lot 14) : les interrupteurs "Rappel de séance" et "Résumé hebdomadaire" (settings.notificationPrefs.seance et .resume), lus par aucun code, sont retirés de l'écran Réglages ; seul "Repos terminé" (lu par le minuteur de repos) reste affiché. Rien n'est supprimé ni modifié dans les données : les valeurs stockées et les valeurs par défaut sont conservées (setNotificationPref les réécrit telles quelles), seules les lignes sont cachées (NOTIFICATION_TYPES). À remettre le jour où une notification de séance ou de résumé existera.
* Noté le 2026-10-10 (lot 14), non corrigé : le calculateur de disques (buildPlateCalcPanel et buildPlateSetEditor) n'est appelé nulle part. Il suit maintenant la barre et les disques réglés, mais reste du code inutilisé.

* Noté le 2026-10-10 (lot 13), non corrigé : la feuille "Jours" de l'éditeur de routine enregistre par OvrykDB.updateRoutine, qui avance routine.updatedAt. La séance suivante de cette routine ne reprend alors plus la dernière séance (routineEditedSinceLastSession dans buildSessionFromRoutine) : charges et reps cibles de la double progression repartent de la routine, alors que seul le jour a changé. Aucune donnée perdue. "Déplacer une séance" (lot 13) évite ce cas en n'écrivant que weekdays. À décider : faire pareil dans la feuille "Jours".

## Réglages sans interface

* settings.restByType ({ technique: 150, force: 120, muscu: 90 }, lot 10, R10) : toujours sans écran de réglage (lot 14, livraison 5, en attente) ; seul addExercisesToRoutine le lit pour l'instant (repos par défaut à l'ajout d'un exercice dans une routine). Pas d'écran de réglage dans ce lot — à exposer plus tard (lot 14, Réglages et matériel, est le candidat naturel).

## Idées non traitées

* Accès au détail d'un cycle (openCycleDetailPage) : fait pour "Tes N cycles" et Coordination (point E, 2026-10-09), puis pour l'Accueil (lignes de cycle de la carte de séance, tuile "Prochain test 1RM") et le panneau du jour (Programme et Accueil, buildProgrammeDayPanelCard) au lot 12 (2026-10-10). Reste à faire si souhaité : depuis la séance en cours (buildHalteroLiveBody n'a aucun lien vers la vue complète du cycle ; le lot 12 n'y touche pas).
* Retrait possible des flèches monter/descendre dans l'éditeur de routine, devenues redondantes depuis le glisser-déposer (lot 09, livraison 3). Noté le 2026-10-10, pas encore retiré : à confirmer avant de supprimer une fonction existante (règle 9).

* Exercice à un seul haltère (ex. "Rowing haltère unilatéral") : la carte de chargement affiche "2 haltères de X kg". Un drapeau unilatéral par exercice serait nécessaire (lot 17, décision 3A : weightKg reste le poids d'un haltère). Noté le 2026-10-10.

## Points de livraison utiles

* Après le lot 03 : l'application a l'allure de la maquette.
* Après le lot 05 : tu peux t'entraîner avec le nouveau mode haltérophilie.
* Après le lot 08 : le système de cycles est complet.
* Après le lot 14 : plus rien à régler dans le code.

* Corrigé le 2026-10-10 : cloneSetsFromPastSex recopiait result, repResults, failRep, failCause et repsDone d'une ancienne série (visible avec "Refaire cette séance" ou une séance relancée sur un mouvement d'haltérophilie sans cycle) ; ces champs repartent à null, comme dans cloneSessionSet. Les séances passées ne sont pas touchées. L'Historique ignore aussi une séance sans exercises ou un exercice null (getExerciseSessionRecords, historyExercises).
* Noté le 2026-10-10, non corrigé : une séance sans tableau exercises fait encore planter computeWeeklySeriesCounts (onglet Progrès) et d'autres lecteurs de session.exercises. Données mal formées seulement, aucune séance réelle n'est concernée.
* Noté le 2026-10-10 (lot 17, livraison 5), non corrigé : dans un superset ou un circuit, l'éditeur affiche "Enchaîné, sans repos" pour les membres sauf le dernier, mais la séance lance quand même le repos (sex.restSeconds) à chaque série validée. La liste de séance écrit seulement "Enchaîné avec l'exercice suivant". Changer le repos touche R10 : à décider.
* Noté le 2026-10-10 (lot 17, livraison 5) : styles .live-session-header-row et .live-set-check (ancien tableau à coche) ne sont plus utilisés par aucun code ; laissés en place, sans effet.
* Noté le 2026-10-10 (lot 17, livraison 5), comportement d'avant gardé : buildCycleTestForm pose sex.testAttempts = [] en mémoire à l'affichage de la carte de test (écrit avec la séance à la première action suivante). Champ existant depuis le lot 05.
* Fait le 2026-10-10 (hors lot, interface seule, sw v112) : éditeur de routine, ligne d'un exercice de muscu. Quand toutes les séries ont les mêmes valeurs (même type de reps, mêmes reps ou même plage, même poids), la ligne montre des champs reps (min à max) et kilos modifiables, appliqués à toutes les séries (buildRexInlineEditRow) ; la flèche ouvre toujours l'écran de réglages. Séries différentes (pyramide, dégressif) : résumé et tap vers l'écran de réglages, comme avant. Écriture au "change" d'un champ seulement (OvrykDB.updateRoutine), aucune à l'ouverture. Cette ligne à champs uniques a été retirée en v113 ; le comportement réel des champs de buildSetRow est décrit à la note de la v115 plus bas. Aucun champ ajouté. Écran de réglages vérifié, inchangé : "Palier de montée" et "Progression automatique" y sont visibles pour un exercice de muscu, y compris dans une routine en création et pour un exercice sans historique.
* Noté le 2026-10-10 : les mouvements d'haltérophilie sans cycle gardent leur tableau de séries en ligne (inchangé) ; la ligne d'édition directe ne concerne que la muscu.
* Modifié le 2026-10-10 (hors lot, interface seule, sw v113) : éditeur de routine, exercice de muscu. À la demande de Ruben, le bloc "Séries" (stepper) et le tableau des séries (kg, reps ou plage, une ligne par série), jusque-là dans l'écran de réglages, sont aussi directement dans l'éditeur, comme pour l'haltérophilie sans cycle. Cela remplace la ligne à champs uniques ajoutée en v112 (buildRexInlineEditRow, retirée, ainsi que buildRexSummaryText devenu inutile) : le tableau gère aussi les séries différentes. Une ligne "Réglages : palier de montée, progression automatique" ouvre l'écran de réglages, qui garde tout son contenu. Mêmes champs et mêmes écritures qu'avant (OvrykDB.updateRoutine au "change"), aucune écriture à l'ouverture.
* Modifié le 2026-10-10 (hors lot, interface seule, sw v115) : champs kilos, reps, min et max de buildSetRow (éditeur de routine et écran de réglages d'un exercice), via commitSetNumber. Un champ vidé ou non numérique remet la valeur précédente dans le champ et n'écrit rien (jamais de null écrit sur une valeur existante) ; une série neuve sans valeur peut rester vide. Plage : un min supérieur au max, ou un max inférieur au min, est refusé : valeur précédente remise, message "Le minimum ne peut pas dépasser le maximum" sous la ligne pendant 3 secondes, rien d'écrit. Kilos négatifs ramenés à 0, virgule non gérée (champ number du navigateur). Supprimées (aucune référence) : aggregateMin, aggregateMax, allSameDefinedValue. Conservé : le style .live-session-remove-btn, encore posé par le bouton de retrait de la carte de séance (buildLiveCardToolbar). Resté à décider : le bouton Reps/Plage de l'en-tête applique le changement à toutes les séries d'un coup (la plage d'origine est perdue au retour à reps fixes).
* Fait le 2026-10-10 (lot 11, interface seule, sw v116) : séparateur de bloc dans la liste de séance. Calculé à chaque rendu par buildLiveBlockSeparator (getLiveExerciseBlock), aucun champ ni écriture. Le bouton Lancer de la pause de 3 min n'écrit rien non plus : il démarre la barre de repos existante (startRestTimer), qui a déjà son bouton Passer. Le bloc "Ce qui change" de la maquette est retiré (demande de Ruben, v117). Pas de séparateur en tête de liste, dans un superset ou circuit, ni sans changement de bloc. Récapitulatif du bloc qui précède : l'enchaînement d'exercices du même bloc juste avant, charge max et résultat ("en cours" tant qu'une série reste à faire). Noté : la pause n'est pas un compte à rebours dans la carte, c'est la barre de repos qui l'affiche.
