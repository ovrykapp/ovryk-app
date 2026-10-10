# LOT 17. Séance sur un seul écran

Taille : L. Dépend de : 05, 09, 10. Lot à risque (séance en cours, R6, R12, test de 1RM) : un seul plan pour tout le lot, approbation, puis toutes les livraisons à la suite.

Cadrage rédigé et validé le 2026-10-10. Décisions prises : 1A, 2A, 3A (fin de ce fichier). L'ancien écran un exercice à la fois est retiré sans option, à la livraison 5 seulement.

## Avancement

* Livraison 1, chargement selon le matériel : faite (commit 79f7ca1, sw v101).
* Livraison 2, cartes repliables et état déplié : faite (32798c0, sw v102).
* Livraison 3, muscu, cercle et saisie dans la ligne : faite (b5cc49a, sw v103).
* Livraison 4, haltérophilie, cercle, bouton Raté, dé-validation : faite (ef62c63, sw v104).
* Corrections hors livraison (862b20f, sw v105) : 1. muscu à reps fixes, le cercle écrit repsActual et non plus set.reps (la prescription recopiée par la séance suivante) ; getMuscuSetReps lit repsActual sinon reps, et la séance suivante remet repsActual à null sur une série fixe recopiée. 2. "+ Ajouter une série" remet result, repResults, failRep, failCause, repsDone et repsActual à null dans la copie. 3. La série en cours reste visible au dessus de la barre de repos (scroll-margin selon la hauteur réelle de la barre). 4. Le rappel "Meilleur" ne lit que les séances terminées.
* Livraison 5 : faite le 2026-10-10 (sw v111), après la séance test de Ruben avec le nouvel écran (cercle, minuteur, saisie avec virgule, moins de reps que prévu, dé-validation : RAS). Contenu :
  * Semaine de test : le formulaire de tentatives (buildCycleTestForm), ou l'avis "test déjà validé" (buildCyclePendingNotice), passe en tête de carte à la place du tableau. Les séries de montée prescrites (40 %, 60 %... jusqu'aux singles) restent dessous sous "Séries de montée", avec leurs cercles : les retirer aurait supprimé une fonction (règle 9). Même condition d'affichage qu'avant (getCycleWeek(cycle).isTestWeek).
  * Avis R12 "Séance légère" dans l'en-tête de la carte dépliée, sous "Série X sur N" (avant : dans le corps haltérophilie).
  * Supersets et circuits encadrés dans la liste (findConsecutiveGroups, comme l'éditeur), intitulé Superset ou Circuit, "Enchaîné avec l'exercice suivant" entre les membres. Le repos n'est pas changé (voir PLAN.md).
  * Emplacement du séparateur du lot 11 : buildLiveBlockSeparator(précédent, suivant), appelé entre deux exercices consécutifs, bloc lu par getLiveExerciseBlock (cycle ou haltérophilie, sinon muscu). Ne renvoie rien tant que le lot 11 n'est pas fait.
  * Objectif du jour d'une série muscu à reps fixes : ses reps prévues (getMuscuDefaultReps), plus de "- reps" ; la ligne "Plage" seulement pour une série en plage.
  * "Série X sur N" en bleu sur une carte de cycle ou d'haltérophilie.
  * Code de l'ancien écran retiré après recherche dans tout index.html (aucun autre appel ni nom en chaîne) : buildLiveSessionExercise, buildLiveSessionHeader (et son bouton retirer en double), buildLiveSessionNextHint, buildLiveAdvanceBanner, goToLiveExercise, liveAdvanceTimeoutId et cancelLiveAdvance (jamais armé, ses 6 appels étaient sans effet), failSheetIndex et le paramètre index d'openFailSheet, styles .live-session-exercise, .live-session-name, .live-session-top-header, .live-session-next-row, .live-advance-banner.
  * Testé avec l'export de backups/ : séance UPPER B en cours ouverte sans écriture, une série validée, rechargement, reprise avec toutes les séries et les mêmes clés. Séance de test synthétique : formulaire avant les séries de montée, avis R12, superset encadré, objectif à reps fixes, aucune erreur JavaScript.

Précisions de Ruben intégrées (2026-10-10) :

* Le cercle valide avec les valeurs préremplies (poids prescrit, reps cibles) sans retaper ; une valeur modifiée avant le tap est celle qui est écrite. Conséquence : une série muscu en plage validée sans retaper prend les reps cibles affichées (targetReps, sinon repsMin) dans repsActual. Avant, "Valider la série" laissait repsActual vide et R5 ignorait la série.
* Une carte repliée se rouvre au tap, jamais deux cartes dépliées.
* Dé-valider ne relance ni le repos ni l'avance d'exercice, et ne fausse ni R5 (la série dé-validée a done = false, donc exclue) ni la fin d'exercice (recalculée à chaque rendu).
* Une série validée non modifiée écrit les mêmes champs que les anciens boutons. Vérifié sur l'export de backups/ : mêmes clés de série et d'exercice avant et après.
* Une séance en cours au moment de la mise à jour s'ouvre sans migration (testé avec la séance UPPER B en cours de l'export, et en rechargeant la page en pleine séance).

Prévu pour la livraison 5 (fait, voir plus haut) : test de 1RM (formulaire de tentatives dans la carte, à la place du tableau), avis R12 dans l'en-tête de la carte, supersets et circuits encadrés, emplacement du séparateur du lot 11, retrait du code de l'ancien écran (buildLiveSessionExercise, buildLiveSessionHeader, buildLiveSessionNextHint, buildLiveAdvanceBanner, goToLiveExercise, liveAdvanceTimeoutId, styles .live-session-top-header et .live-session-next-row). À voir aussi : la barre de repos, collée en bas, cache la série suivante (il faut défiler) ; le compteur "Série X sur N" de la carte reste orange sur une carte de cycle.

## Écrans de la maquette

* ../maquette/02-seance-muscu.png et ../maquette/03-seance-halterophilie.png, à adapter : elles montrent un exercice à la fois avec un bouton "Valider la série" plein largeur. Ce lot garde leurs blocs (rappels, charge, chargement, séries) mais les range dans une liste unique.
* ../maquette/10-haltero-un-rate.png et ../maquette/11-haltero-serie-longue.png : la feuille "Un raté" et le compteur de reps restent tels quels.

## Objectif

Besoins exprimés par Ruben :

1. Au lancement d'une séance, voir tous les exercices de la séance sur un même écran.
2. Valider chaque série avec un cercle placé à droite de la série.
3. Le chargement affiché doit tenir compte du matériel de l'exercice (barre, haltères, autre).

## Existant à connaître

* renderSeanceActiveView n'affiche qu'un exercice : activeSession.exercises[liveSessionIndex]. liveSessionIndex vit en mémoire seulement (jamais enregistré), recalculé par computeInitialLiveExerciseIndex (premier exercice non terminé).
* buildLiveSessionExercise choisit buildHalteroLiveBody (catégorie Lifting) ou buildMuscuLiveBody. buildLiveSessionHeader (chevron précédent, "Exercice X sur N", bouton retirer), buildLiveSessionNextHint ("Ensuite"), goToLiveExercise.
* Avance automatique : liveAdvanceTimeoutId, 2,5 s après la dernière série, bannière buildLiveAdvanceBanner avec "Annuler", cancelLiveAdvance.
* Muscu : buildLiveObjectiveCard, buildMuscuSetsTable, buildMuscuSetRow (colonnes N, Précédent, kg, reps, coche ; taper la coche d'une série validée la dé-valide, set.done = false), bouton "Valider la série" (live-validate-row), "+ Ajouter une série".
* Haltérophilie : buildLightSessionNotice (R12), rappels Dernière fois / Meilleur, buildHalteroChargeCard (-2,5 / +2,5 et pastilles de %, écrit set.percent1rm), buildHalteroSetsTable, buildHalteroCounterCard (R6, 4 reps et plus), feuille "Un raté" (openFailSheet : result, repResults, failRep, failCause, done), buildHalteroNoteField (set.note).
* Test de 1RM : buildCycleTestForm dans le corps haltérophilie quand getCycleWeek(cycle).isTestWeek, tentatives, feuille test-attempt-fail-overlay, cycleTestSubmittedIds. buildCyclePendingNotice si le cycle attend validation.
* Popup de semaine de test (livraison E) : launchRoutineSession appelle resolvePendingCycleTestChoices avant buildSessionFromRoutine, donc avant tout affichage de séance.
* Repos : startRestTimer(nom, secondes), barre rest-timer-bar en bas d'écran, déjà indépendante de l'exercice affiché.
* Chargement : buildPlateLoadCard (toujours une barre, BAR_WEIGHT_KG = 20), buildMuscuLoadCard (Barre ou vide : plaques ; Haltères : "2 haltères de X kg" ; Poulie, Machine, Poids du corps, Autre : rien). L'haltérophilie appelle buildPlateLoadCard directement, sans regarder exercise.equipment. EQUIPMENT_LIST = Barre, Haltères, Poulie, Machine, Poids du corps, Autre.
* Supersets et circuits : sex.groupId, sex.groupType, déjà copiés de la routine.

## 1. Structure de l'écran (390 px)

De haut en bas, une seule page qui défile :

1. Barre du haut, collante (existante, inchangée) : nom de la séance, chronomètre, "Terminer".
2. Ligne d'avancement : "2 exercices sur 6 terminés" et une barre fine. Couleur bleue pour le bloc cycle, orange pour la muscu.
3. Liste des exercices, dans l'ordre de la séance. Les membres d'un superset ou d'un circuit sont encadrés ensemble, avec la mention "enchaîné, sans repos" entre eux, comme dans l'éditeur. Le lot 11 insérera ici un séparateur de bloc (voir point 3).
4. En bas de liste : notes de la séance, "+ Ajouter un exercice", "Terminer la séance".
5. Minuteur de repos : la barre rest-timer-bar existante, collée en bas, au-dessus de tout. Elle se lance au tap d'un cercle, comme aujourd'hui avec la coche.

### Carte d'exercice repliée (par défaut pour tous sauf l'exercice actif)

Une ligne de 56 px environ : nom (et prise), étiquette "Cycle N, semaine X" en bleu ou "Muscu" en orange, résumé de la prescription ("4 x 3 à 82 kg", "3 x 8 à 10 à 60 kg"), compteur "2/4". Exercice terminé : cercle plein à droite et résumé des résultats ("4/4 réussies", "10, 9, 8 reps"). Taper la ligne déplie la carte et en fait l'exercice actif.

### Carte d'exercice dépliée (l'exercice actif)

* En-tête : nom, étiquette, bouton retirer (existant, avec confirmation). Avis "Séance légère" (R12) si sex.isLightSession.
* Rappels sur une ligne : Dernière fois, Meilleur.
* Tableau des séries. Colonnes à 390 px (largeur utile 334 px environ) : N (28 px), Précédent (64 px), kg (1fr), reps (1fr), cercle (44 px, zone de tap 44 x 44).
  * Série en cours : bordure de couleur, champs kg et reps éditables en ligne (clavier numérique). En haltérophilie, la colonne kg affiche la charge et le %, le réglage fin (-2,5 / +2,5, pastilles de %) est replié sous la ligne dans "Ajuster la charge".
  * Séries à venir : grisées, valeurs prévues, cercle vide.
  * Séries faites : valeurs réelles, cercle plein (coche). Raté en haltérophilie : cercle à bord orange avec la rep ratée ("Raté à la 2").
  * Série de 4 reps et plus en haltérophilie (R6) : la colonne reps devient un compteur de reps réussies, prérempli au nombre prévu ; le cercle valide avec ce compte.
  * Note de série : petite icône crayon dans la ligne, champ replié par défaut, ouvert d'office s'il y a déjà une note.
* Sous la série en cours, une ligne "Chargement" selon le matériel (point 1 ci-dessous), le schéma des disques replié.
* "+ Ajouter une série".
* Semaine de test (cycle en test, isTestWeek) : la carte affiche le formulaire de tentatives existant (buildCycleTestForm) à la place du tableau. Pas de cercle sur les tentatives, qui gardent leurs boutons réussie et ratée.

### Exercice actif

* Au lancement : le premier exercice qui a une série non faite (computeInitialLiveExerciseIndex, inchangé).
* Après la dernière série d'un exercice : sa carte se replie, la suivante se déplie et défile en haut de l'écran. Plus de délai de 2,5 s ni de bannière "Annuler" : rien n'est perdu, l'exercice terminé reste à un tap.
* Un seul exercice déplié à la fois. On peut déplier n'importe quel exercice, fait ou à venir (remplace le chevron "précédent" et la ligne "Ensuite").
* L'exercice déplié n'est pas enregistré dans la séance : il reste en mémoire (liveSessionIndex), comme aujourd'hui.

### Chargement selon le matériel

Une seule fonction d'affichage, lue partout (muscu et haltérophilie), à partir de exercise.equipment :

* Barre, ou matériel absent (exercices anciens) : charge par côté, "Par côté : 20 + 5 + 1,25, barre de 20 kg" (computePlateLoad). Le poids de barre passe par cette fonction seulement, pour que le lot 14 (settings.barWeightKg) n'ait qu'un endroit à changer.
* Haltères : "2 haltères de X kg" (sens actuel de weightKg, voir décision 3).
* Machine, Poulie : "Charge X kg", sans disques.
* Poids du corps : "Poids du corps", et "+ X kg de lest" si une charge est saisie.
* Autre : "X kg au total".
* Haltérophilie : même fonction. Un mouvement Lifting sans matériel renseigné reste traité comme une barre (comportement actuel).

## 2. Ce qui change et ce qui reste

Change :

* Un exercice à la fois devient une liste de cartes repliables.
* Le bouton plein largeur "Valider la série" et "Série réussie" disparaissent : le cercle à droite de la ligne valide.
* Chevron précédent, "Exercice X sur N", ligne "Ensuite", avance automatique à 2,5 s et sa bannière : remplacés par le dépliage et le défilement.
* Saisie du poids et des reps directement dans la ligne de la série en cours.
* Le chargement de l'haltérophilie tient compte du matériel.

Reste identique :

* Toutes les données de séance et la façon de les écrire (mêmes champs, mêmes fonctions de calcul, persistActiveSession à chaque action).
* La construction de la séance (buildSessionFromRoutine), la popup de semaine de test, R5, R6, R12, le test de 1RM et ses tentatives.
* La feuille "Un raté", le compteur de reps, la note de série, la double progression et son objectif, la suggestion de baisse.
* Le minuteur de repos et ses durées (R10), la barre du haut, "Terminer", la fin de séance, l'ajout et le retrait d'exercice.
* Dé-valider une série muscu en retapant son cercle (existant avec la coche).

## 3. Impacts

* Séances en cours : une séance démarrée avant la mise à jour a exactement le même format ; elle s'ouvre directement dans la liste, l'exercice actif est le premier non terminé. Aucune migration. À tester avec une séance en cours dans l'export de backups/ et en rechargeant la page au milieu d'une séance.
* R12 (deuxième séance de la semaine, plus légère) : rien ne change dans le calcul (buildCycleSessionSets, isLightSession). L'avis "Séance légère" passe dans l'en-tête de la carte concernée, et l'étiquette repliée le signale ("Cycle 4, sem. 3, légère"). Note : la séance allégée par décharge de la muscu est R8 (lot 13, pas encore construite) ; quand elle arrivera, son avis "Séance allégée" avec "Ignorer" ira en haut de la liste, pour toute la séance.
* Popup de semaine de test (livraison E) : aucun impact, elle s'ouvre avant la construction de la séance. Si le test est fait, la carte du mouvement montre le formulaire de tentatives. Si le test est repoussé ou le cycle changé, la carte montre des séries normales.
* Lot 11 (séparateur de bloc) : son écran de transition plein écran perd son sens dans une liste. Il devient un séparateur dans la liste, entre le dernier exercice du bloc cycle et le premier de la muscu : récapitulatif du bloc terminé, "Ce qui change", pause conseillée de 3 minutes. Son risque "ne pas réafficher un séparateur déjà passé" disparaît. LOT-11.md sera à réécrire en conséquence après ce lot, d'où l'ordre 17 puis 11.

## 4. Risques pour les données

* Aucun champ de séance, d'exercice de séance ou de série n'est ajouté, renommé ou supprimé. Le cercle écrit exactement ce qu'écrivent aujourd'hui la coche, "Valider la série", "Série réussie" et la feuille "Un raté" : done, weightKg, reps, repsActual, result, repResults, repsDone, failRep, failCause, percent1rm.
* Saisie en ligne : un champ vidé ou invalide ne doit jamais écrire NaN ni null par-dessus une valeur prévue. Même règle de lecture qu'aujourd'hui.
* Tap involontaire : un cercle est plus petit qu'un bouton plein largeur. Garder la zone de 44 px, et la dé-validation possible pour corriger.
* Dé-valider une série d'haltérophilie ratée : aujourd'hui non prévu. Voir décision 2 (efface ou non result, repResults, failRep, failCause).
* Séances passées : jamais réécrites (règle 6). L'écran de séance ne touche que activeSession.
* Le test de 1RM, avec ses écritures sur le cycle (one_rm_actuel, historique_cycles, prochain_cycle), reste dans sa fonction actuelle, sans changement.
* Plus d'avance automatique : aucune donnée n'en dépend (liveAdvanceTimeoutId est en mémoire seulement).
* Tests sur la copie locale avec l'export de backups/, jamais sur l'app installée. Exporter, réimporter et comparer avant et après une séance faite sur le nouvel écran.

## 5. Découpage en livraisons

1. Chargement selon le matériel : une seule fonction d'affichage, utilisée par l'écran actuel en muscu et en haltérophilie. Interface seule (affichage, aucune écriture).
2. Liste des exercices : cartes repliées avec résumé et état, l'exercice actif déplié en réutilisant les corps actuels (buildMuscuLiveBody, buildHalteroLiveBody), dépliage au tap, suppression du chevron, de "Ensuite" et de l'avance automatique. À risque (séance en cours), sans nouvelle écriture.
3. Muscu : tableau avec saisie en ligne et cercle à droite, bouton "Valider la série" retiré, dé-validation au cercle. À risque (écrit les séries).
4. Haltérophilie : cercle "réussie", raté (selon décision 1), compteur pour 4 reps et plus, "Ajuster la charge" replié, note de série. À risque (R6).
5. Test de 1RM et R12 dans les cartes, supersets et circuits encadrés, emplacement du séparateur du lot 11, repli et défilement automatiques, retrait du code de l'ancien écran devenu inutile. À risque.

Chaque livraison : node --check, verifier-cycles.js, smoke.py, vérification à 390 x 844, version du cache sw.js augmentée, commit local.

## Données

Aucune.

## Règles métier concernées

R5, R6, R10, R12. R3 pour le test de 1RM (affichage seulement). R8 plus tard (lot 13).

## Critères d'acceptation

* Au lancement d'une séance de 6 exercices, les 6 sont visibles sur un écran, le premier déplié.
* Chaque série se valide avec le cercle à sa droite, qui lance le repos de l'exercice.
* Après la dernière série d'un exercice, le suivant se déplie sans action.
* Une série d'haltérophilie se valide réussie en un tap, un raté enregistre rep et cause (R6), une série de 5 reps passe par le compteur.
* Le chargement affiche les disques par côté pour une barre, "2 haltères de X kg" pour des haltères, rien de faux pour une machine, une poulie ou le poids du corps.
* Une séance en cours, démarrée avant la mise à jour, s'ouvre sans erreur et se termine normalement.
* La semaine de test affiche les tentatives dans la carte du mouvement, et la fin de cycle s'enchaîne comme avant.
* Export avant et après une séance faite sur le nouvel écran : mêmes champs, aucune valeur NaN ou undefined.

## Hors lot

* Le séparateur de bloc lui-même (lot 11).
* La décharge de la muscu (lot 13) et le poids de barre configurable (lot 14).
* Réordonner les exercices pendant la séance.

## Décisions de Ruben (prises le 2026-10-10 : 1A, 2A, 3A)

1. Haltérophilie : comment déclarer un raté, puisque le cercle valide une série réussie ?
   A. Un petit bouton "Raté" à gauche du cercle, sur la série en cours (recommandé : visible, aucun geste caché).
   B. Un appui long sur le cercle.
2. Retaper le cercle d'une série d'haltérophilie déjà ratée : faut-il la dé-valider en effaçant result, repResults, failRep et failCause (séance en cours seulement, comme la muscu aujourd'hui) ?
   A. Oui, la série redevient à faire (recommandé : on corrige une erreur de saisie).
   B. Non, seule la feuille "Un raté" peut la modifier.
3. Haltères : la charge saisie (weightKg) est-elle le poids d'un haltère ou le total des deux ?
   A. Le poids d'un haltère, comme aujourd'hui ("2 haltères de X kg") ; rien ne change dans les données ni dans l'historique (recommandé).
   B. Le total : il faudrait alors changer l'affichage et le calcul du volume, et décider quoi faire des séances passées.

Rappel (règle 9, suppression d'une fonction existante) : ce lot remplace l'écran un exercice à la fois, sans le garder en option. Si Ruben veut le conserver derrière un réglage, le dire avant le plan.
