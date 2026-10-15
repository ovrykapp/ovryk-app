# LOT 18. Choix de la salle (Indé / On Air) et équivalents d'exercices

Statut (2026-10-16) : TERMINÉ, audité par Opus (verdict SÛR, aucun bloquant), POUSSÉ, tag v142-stable ; les six décisions prises pendant le lot sont validées par Ruben ; reste sa validation iPhone. Les mentions « en local, non poussée » plus bas sont périmées (poussé avec v142-stable).

Taille : M. Dépend de : 09, 10, 13, 17. Lot à risque (construction des séances, séance en cours, double progression) : un seul plan, approuvé le 2026-10-15. Conditions de Ruben : pas d'enchaînement, rapport et arrêt après chaque livraison ; rien n'est poussé avant la fin de la livraison 3, un audit Opus en lecture seule des 3 commits et les tests manuels. La livraison 2 n'est jamais poussée seule.

## Objectif

Ruben s'entraîne dans une salle indépendante, où il manque des machines, et à On Air, où tout est là. Aujourd'hui, il duplique ses routines en "(indé)", sans jour planifié. Le lot remplace ce contournement : on choisit la salle au lancement de la séance, et chaque exercice peut avoir un "équivalent en salle indé", qui le remplace quand la séance est construite en salle indé. Aucune migration des routines "(indé)" : Ruben les supprimera lui-même.

## Modèle de données (champs optionnels, aucune nouvelle clé de stockage)

* exercise.gymEquivalentId : chaîne, null (équivalent retiré) ou absent (jamais défini). L'exercice à faire à la place en salle indé. Écrit seulement depuis l'écran "Équivalent en salle indé" de la fiche exercice.
* session.gym : 'inde' ou 'onair', absent pour une séance d'avant ce lot (livraison 2).
* sex.replacesExerciseId : sur l'exercice d'une séance, l'exercice de la routine qu'il remplace (livraison 2).
* Dernière salle utilisée : déduite de la séance la plus récente qui a un champ gym, On Air par défaut. Aucune clé, aucune écriture au lancement.
* Noms de salle : constantes du code (Indé, On Air), pas de réglage.
* schemaVersion inchangé (2), migrateSchema inchangé. Empreinte : calculée sur les données comme avant, les nouveaux champs en font partie quand ils existent. validateBackupFile, getBackupCrashError, import, restauration par fichier et en ligne, copies quotidiennes : inchangés. Un ancien export sans les champs reste restaurable tel quel.

## Règles

* getGymEquivalent (lecture seule) : l'équivalent n'est utilisé que s'il existe, n'est pas l'exercice lui-même, et si ni la source ni la cible ne sont des mouvements (Lifting). Un seul saut, jamais de chaîne.
* Refusés à l'enregistrement, avec un message, et affichés comme non disponibles dans la liste :
  * un exercice qui est déjà l'équivalent d'un autre ne peut pas avoir lui-même un équivalent ;
  * l'exercice lui-même et les mouvements (Lifting) ne sont pas proposés ;
  * une cible qui a déjà son propre équivalent ;
  * le contrôle est refait au moment d'écrire (l'état a pu changer entre le choix et "Enregistrer").
* Équivalent introuvable (seulement possible après l'import d'un fichier où la cible manque, l'app ne supprime jamais d'exercice) : la fiche affiche "Équivalent introuvable", l'exercice d'origine reste utilisé.
* Structure du créneau (séries, plage de reps, repos) : celle de la ligne de routine. Charges et double progression : historique de l'équivalent dans la même routine (livraison 2).
* Doublon (l'équivalent est déjà dans la routine) : deux cartes, la carte de remplacement porte "remplace X" ; chaque carte est retrouvée par son créneau (exerciseId plus replacesExerciseId), compteurs et records ne comptent une séance qu'une fois (livraison 2).
* Sélecteur de salle (livraisons 2 et 3) : pilule role="switch", aria-label "Salle", Graphite avec bordure de 1 px en --neutral-400, pastille Rouille, nom actif en Graphite (le Chalk sur Rouille fait environ 2,5:1), animation CSS seulement, désactivée sous prefers-reduced-motion. Verrouillée dès la première série validée.

## Limites acceptées (2026-10-15)

1. Les charges de l'équivalent ne sont lues que dans la même routine : un équivalent fait dans une autre routine ne pré-remplit pas les charges.
2. En cas de doublon, le "dernière séance" d'une carte de remplacement aurait été pris sur la première carte Y de la séance. Limite levée en livraison 2b par la règle du créneau (findSexForSlot) : chaque carte a son propre "dernière séance", sa propre progression et sa propre suggestion de baisse.
3. Décision du 2026-10-15, appliquée en 2b : sans historique de l'équivalent dans la routine (ni carte de ce créneau, ni carte normale de l'équivalent), la carte remplacée garde la structure du créneau (séries, plage, repos) avec des charges vides, jamais celles de l'exercice d'origine. Avec une carte normale de l'équivalent dans la routine, la charge de départ est la sienne (première série faite).
4. La suggestion de baisse et la stagnation ignorent l'ancienneté des séances (comportement existant, non spécifique aux salles).

## Livraisons

1. Modèle et éditeur d'équivalent, sans changement des séances (sw v139).
2. Découpée en deux le 2026-10-15, la livraison étant trop grosse pour un audit propre :
   * 2a : pilule sur l'écran de départ, remplacement à la construction, salle enregistrée et affichée, continuité des charges, allègement automatique (lot 13) vérifié sur une carte remplacée (sw v140) ;
   * 2b : règles du doublon (findSexForSlot) et fusion des statistiques seulement quand une carte porte replacesExerciseId, avec un test "avant et après identiques" sur les séances sans carte remplacée (sw v141).
3. Changement de salle pendant la séance avant la première série (reconstruction ciblée), verrouillage (sw v142).

## Avancement

* Livraison 1 faite le 2026-10-15 (sw v139), en local, non poussée (périmé : poussée avec v142-stable).
  * Fiche exercice (renderExerciseDetailFicheExtra) : ligne "Équivalent en salle indé · nom" (ou "Aucun", ou "Équivalent introuvable"), absente pour un mouvement (Lifting). La fiche de la cible indique "Fait en salle indé à la place de : …".
  * Écran exercise-equiv-page : recherche (normalizeSearch existante), "Aucun équivalent" en tête, choix non disponibles grisés avec leur raison, sélection en orange. Rien n'est écrit avant "Enregistrer" ; "Aucun" sur un exercice qui n'a jamais eu d'équivalent n'écrit rien.
  * OvrykDB.updateExerciseGymEquivalent : n'écrit que l'exercice concerné. Fonctions getGymEquivalent, getGymEquivalentSources, getGymEquivalentError.
  * Aucune séance n'est modifiée : une routine se lance toujours avec l'exercice d'origine, sans salle.
  * Tests : dossier-lots/tests/test_gym.py (19 contrôles, données fabriquées).
* Livraison 2a faite le 2026-10-15 (sw v140), en local, non poussée (périmé : poussée avec v142-stable).
  * Salles : constantes GYMS (Indé, On Air) ; dernière salle utilisée déduite de la séance la plus récente qui a un champ gym (getLastUsedGym), On Air par défaut ; aucune clé, aucune écriture au lancement.
  * Écran de départ : pilule (buildGymSwitch, role="switch", aria-label "Salle", texte invisible "Salle actuelle : …"), choix en mémoire jusqu'au lancement (seanceStartGym), "N remplacé(s) en indé" sur chaque ligne de routine. Une bascule n'écrit rien.
  * buildSessionFromRoutine(routine, gym) : session.gym enregistré ; en salle indé, une ligne dont l'exercice a un équivalent (jamais un mouvement de cycle) est construite avec l'équivalent, replacesExerciseId = l'exercice de la routine. Lancements de l'Accueil ("Commencer la séance"), du Programme ("Démarrer") et "Refaire cette séance" : dernière salle utilisée. Séance vide : salle enregistrée, aucun remplacement.
  * Continuité : pour un exercice concerné par un équivalent (il en a un, ou il en est un), la reprise lit la dernière séance de la routine qui le contient (getLastCompletedRoutineSessionWithExercise) ; tous les autres exercices : inchangé (dernière séance de la routine).
  * Structure et charges d'une carte remplacée : reprise habituelle de la dernière séance de la routine avec l'équivalent (cloneSetsFromPastSex) ; sans historique de l'équivalent dans la routine, la ligne de routine de l'exercice d'origine (séries, plage, repos et charges, voir limite 3).
  * Allègement automatique (lot 13) : vérifié, aucun réglage nécessaire. applyMuscuDeload tourne après la construction et traite la carte remplacée comme toute carte de muscu (type de l'équivalent) ; à la séance suivante, les séries retirées sont remises et la charge reste figée (cloneSetsFromPastSex sur une référence allégée).
  * Affichage : "Salle : …" dans l'en-tête de la séance en cours (lecture seule, livraison 3 pour le changement), "Remplace X (salle indé)" sur la carte, salle dans la liste et le détail de l'historique, "remplace X" sur l'exercice remplacé. Rien pour une séance d'avant ce lot.
  * smoke.py : le contrôle "une séance vide démarre" cliquait sur le premier bouton de l'onglet Séance, devenu la pilule ; il vise maintenant #seance-start-empty-btn.
  * Observé (test G17, retour en salle indé après 10 semaines à On Air) : la carte de l'équivalent repart de sa dernière séance dans la routine (charges, plage, cible de reps de la double progression), sans tenir compte du temps écoulé. La suggestion de baisse (deux dernières séances sous la plage) et la stagnation (trois dernières séances sans progrès) ne regardent que les séances de l'équivalent, quelle que soit leur ancienneté : elles s'affichent encore après 10 semaines si les dernières séances de l'équivalent les déclenchaient.
  * Tests : test_gym.py, 39 contrôles (G10 à G18 ajoutés, G7 adapté : la séance porte maintenant sa salle).
* Livraison 2b faite le 2026-10-15 (sw v141), en local, non poussée (périmé : poussée avec v142-stable).
  * findSexForSlot(session, exerciseId, replacesId) : une carte se reconnaît par exerciseId plus replacesExerciseId ; sans replacesId, la première carte sans replacesExerciseId (dans une séance sans carte remplacée : la même que findExerciseInSession).
  * Double progression (buildSessionFromRoutine) : pour un exercice concerné par un équivalent, dernière séance de la routine qui contient ce créneau (getLastCompletedRoutineSessionWithSlot), carte de ce créneau. Exercices non concernés : inchangés (findExerciseInSession sur la dernière séance de la routine).
  * Carte remplacée sans reprise possible : structure du créneau, charges de getReplacementStartWeight (créneau, sinon carte normale de l'équivalent dans la routine), sinon vides. Une série se valide normalement avec un poids saisi.
  * Comparateur "Précédent" (getLastLoggedSex) et suggestion de baisse (checkDeloadSuggestion) : reçoivent replacesExerciseId de la carte ; sans carte remplacée dans l'historique, résultat identique.
  * Statistiques : getExerciseSessionRecords ne fusionne les cartes d'un même exercice dans une séance que si l'une porte replacesExerciseId (mergeSessionRecords : séries réunies, volume additionné, charge et 1RM estimé maximaux, RPE moyen sur toutes les séries, allégé si l'une l'est) ; countSessionsForExercise compte alors la séance une fois ; toutes les autres séances : un enregistrement et un compte par carte, comme avant. Graphique, 1RM estimé, "Meilleur", stagnation et "Record" de l'historique suivent. Le détail de l'historique compte un record une fois pour un exercice présent en carte normale et en carte remplacée.
  * "+ Séance vide" passe en bouton secondaire (contour Rouille, sans fond), la capture à 390 px montrant qu'il concurrençait la pilule.
  * Tests modifiés : G11 (charges vides au lieu des charges de l'exercice d'origine, décision du 2026-10-15).
  * Tests : test_gym.py, 53 contrôles. G19 charges vides et validation avec un poids saisi, exercice non concerné inchangé ; G20 prévisionnel de la charge de la semaine en Indé et en On Air ; G21 doublon (deux cartes distinctes, progression par carte sur deux séances, comparateur et suggestion par carte, enregistrement sans écrasement, une ligne d'historique par séance, record compté une fois) ; G22 comparaison avec c81f6fe : enregistrements, compteur, comparateur et suggestion identiques sur des séances sans carte remplacée (dont le même exercice deux fois), seule la séance avec une carte remplacée est fusionnée.

* Livraison 3 faite le 2026-10-15 (sw v142), en local, non poussée (périmé : poussée avec v142-stable).
  * Pilule de salle en tête de la séance en cours (même composant et même style que l'écran de départ), avec "Salle : …" toujours dans la barre du haut. Aucune pilule pour une séance sans salle (créée avant ce lot).
  * Verrou : calculé à chaque rendu (isSessionGymLocked), dès qu'au moins une série de la séance est validée. Pilule non cliquable (aria-disabled), atténuée, texte "Salle fixée après la première série.". Dé-valider la dernière série validée déverrouille la pilule (comportement voulu : rien n'est encore fait dans la séance).
  * Changement de salle : buildGymSwitchedExercises construit la nouvelle liste de cartes sans rien modifier, puis switchActiveSessionGym assigne la liste et la salle et écrit une seule fois (persistActiveSession). En cas d'exception pendant la construction : séance intacte en mémoire et en stockage, aucune écriture, message "Changement de salle impossible (la routine de cette séance n'a pas pu être relue). La séance n'a pas été modifiée."
  * Reconstruction ciblée : les cartes issues de la routine sont reconnues dans l'ordre (la n-ième ligne d'un exercice correspond à sa n-ième carte normale ; pour le retour en On Air, à sa n-ième carte de remplacement) ; une carte en plus est un ajout à la main et n'est jamais échangée. Seules les cartes concernées par un équivalent sont reconstruites (buildSessionExerciseFromRex, extraite telle quelle de buildSessionFromRoutine) ; id, début, date, notes, ordre, supersets (groupId et groupType de la carte d'origine), cartes de cycle, ajouts à la main et cartes non concernées (poids et reps saisis compris) restent identiques. Un allègement déjà appliqué à la carte échangée est appliqué de même à la nouvelle carte (même source).
  * Doublon : vers On Air, seule la carte de remplacement redevient X ; vers Indé, seule la carte normale de X devient la carte de remplacement ; la carte Y normale n'est jamais touchée.
  * Perte assumée : poids ou reps saisis à la main sur une carte échangée, sans série validée, sont perdus ; revenir à la salle d'avant reconstruit la carte depuis l'historique ou la routine. Seul effet de bord constaté par les tests (notes, autres cartes, ordre, supersets, minuteur de repos inchangés).
  * Tests : test_gym.py, 69 contrôles (G23 à G31 ajoutés ; aucun test existant modifié par cette livraison).

## Décisions prises pendant le lot, validées par Ruben (2026-10-16)

* Séance fusionnée (doublon avec une carte remplacée) marquée allégée dès qu'une de ses cartes l'est : elle sort alors de la stagnation, comme toute séance allégée.
* Comparateur "Précédent" vide pour une carte remplacée jamais faite dans ce créneau, même si l'équivalent a déjà été fait en carte normale (les charges de départ, elles, se rabattent sur la carte normale).
* Charges vides pour un équivalent sans historique dans la routine (décision de Ruben du 2026-10-15, appliquée en 2b), structure du créneau gardée.
* "+ Séance vide" passé en bouton secondaire (contour) en 2b, la pilule et lui se disputant l'attention.
* Pilule de la séance en cours placée en tête de la vue de séance (zone tactile de 44 px), et non dans la barre du haut trop étroite ; la barre garde "Salle : …".
* Dé-valider la dernière série validée déverrouille la salle.

## Hors périmètre

Bouton Reps/Plage, flèches de l'éditeur, écran du repos par type, gardes de lecture, suite de tests de la restauration locale, migration des routines "(indé)".
