# LOT 18. Choix de la salle (Indé / On Air) et équivalents d'exercices

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
2. En cas de doublon, le "dernière séance" d'une carte de remplacement aurait été pris sur la première carte Y de la séance. Limite levée par la règle du créneau (findSexForSlot, livraison 2b) : chaque carte a son propre "dernière séance". Jusqu'à la 2b, un doublon reste traité par la première carte et compté deux fois dans les statistiques (2a jamais poussée seule).
3. Sans historique de l'équivalent dans la routine, la première carte remplacée reprend les charges de la ligne de routine de l'exercice d'origine (décision du plan) : par exemple 100 kg de presse proposés pour un hack squat. À corriger à la main à la première séance ; la suivante repart de l'historique de l'équivalent.
4. La suggestion de baisse et la stagnation ignorent l'ancienneté des séances (comportement existant, non spécifique aux salles).

## Livraisons

1. Modèle et éditeur d'équivalent, sans changement des séances (sw v139).
2. Découpée en deux le 2026-10-15, la livraison étant trop grosse pour un audit propre :
   * 2a : pilule sur l'écran de départ, remplacement à la construction, salle enregistrée et affichée, continuité des charges, allègement automatique (lot 13) vérifié sur une carte remplacée (sw v140) ;
   * 2b : règles du doublon (findSexForSlot) et fusion des statistiques seulement quand une carte porte replacesExerciseId, avec un test "avant et après identiques" sur les séances sans carte remplacée (sw v141).
3. Changement de salle pendant la séance avant la première série (reconstruction ciblée), verrouillage (sw v142).

## Avancement

* Livraison 1 faite le 2026-10-15 (sw v139), en local, non poussée.
  * Fiche exercice (renderExerciseDetailFicheExtra) : ligne "Équivalent en salle indé · nom" (ou "Aucun", ou "Équivalent introuvable"), absente pour un mouvement (Lifting). La fiche de la cible indique "Fait en salle indé à la place de : …".
  * Écran exercise-equiv-page : recherche (normalizeSearch existante), "Aucun équivalent" en tête, choix non disponibles grisés avec leur raison, sélection en orange. Rien n'est écrit avant "Enregistrer" ; "Aucun" sur un exercice qui n'a jamais eu d'équivalent n'écrit rien.
  * OvrykDB.updateExerciseGymEquivalent : n'écrit que l'exercice concerné. Fonctions getGymEquivalent, getGymEquivalentSources, getGymEquivalentError.
  * Aucune séance n'est modifiée : une routine se lance toujours avec l'exercice d'origine, sans salle.
  * Tests : dossier-lots/tests/test_gym.py (19 contrôles, données fabriquées).
* Livraison 2a faite le 2026-10-15 (sw v140), en local, non poussée.
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

## Hors périmètre

Bouton Reps/Plage, flèches de l'éditeur, écran du repos par type, gardes de lecture, suite de tests de la restauration locale, migration des routines "(indé)".
