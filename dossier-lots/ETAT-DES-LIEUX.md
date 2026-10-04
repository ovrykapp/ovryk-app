# État des lieux d'Ovryk

Source : le fichier index.html de ton projet, dans la version du zip ovryk-maquette (lot 00 fait). Les numéros de ligne changent à chaque lot : cherche toujours par nom de fonction ou d'identifiant.

## Structure du fichier

* Un seul fichier index.html : le style (balise style), le HTML (cinq sections de vue et des pages plein écran), puis le script (JavaScript sans framework).
* La section "SKIN MAQUETTE" à la fin du style contient les surcharges de design du lot 00.
* Application installable : manifest.json, sw.js et les icônes sont dans ton projet, pas dans le fichier envoyé.

## Vues et navigation

| Vue (data-view) | Libellé affiché | Contenu actuel |
|---|---|---|
| dashboard | Accueil | bandeau d'alerte de cycle, bloc "dash-hero" (prochaine routine), cycles en cours, stagnation, résumé de la semaine, dernière séance, progression récente |
| routine | Programme | deux sous onglets : Routines et Exercices (bibliothèque) |
| seance | Séance | choix d'une routine ou séance vide, puis séance active |
| progression | Progrès | groupes musculaires, détail d'un groupe, détail d'un exercice avec historique |
| profil | Réglages | objectifs hebdomadaires, notifications, sauvegarde (export, import), réinitialisation |

Fonctions de navigation : setActiveView, VIEW_LABELS, boutons .nav-btn avec data-target.

Pages plein écran : routine-editor-view, routine-exercise-picker, seance-exercise-picker, cycle-detail-page.

## Modèle de données (localStorage)

Clés : ovryk.exercises, ovryk.routines, ovryk.sessions, ovryk.settings, ovryk.forceCycles.

* Exercice : id, name, category (Pecs, Dos, Épaules, Bras, Jambes, Abdos, Lifting), equipment, unit, isCustom, oneRepMax (Lifting), liftBaseMode ('oly' ou 'force'), forceCycleStartDate, hasGripVariant, lastGrip.
* Routine : id, name, exercises [ { exerciseId, order, restSeconds, groupId, groupType, sets } ], createdAt, updatedAt. Une routine est une séance type. Le commentaire du code parle de "days" mais le code utilise routine.exercises.
* Série de routine : id, repType ('fixed' ou 'range'), reps, repsMin, repsMax, percent1rm (Lifting) ou weightKg.
* Séance : id, routineId, routineName, date, startedAt, completedAt, status ('in_progress' ou 'completed'), durationSeconds, notes, exercises [ { id, exerciseId, exerciseName, category, oneRepMaxSnapshot, restSeconds, groupId, groupType, sets } ].
* Série de séance : id, repType, reps ou repsMin, repsMax et repsActual, percent1rm ou weightKg, done, rpe.
* Cycle de force : exercise_id, cycle_actif ('A' à 'E' ou '1' à '12'), one_rm_actuel, semaine_actuelle, historique_1rm [ { date, valeur } ]. Un seul cycle par mouvement.
* Réglages : unit, restTimerSeconds, lastExportAt, plateSet, muscleGroupTargets, préférences de notifications.

## Ce qui existe déjà et sert aux lots

| Besoin | Existant |
|---|---|
| Prescription depuis un cycle | buildSessionFromRoutine, buildCycleSessionSets, getCycleWeek, FORCE_CYCLES |
| Charge en kg depuis un pourcentage | computeWeightFromPercent (arrondi à 2,5 kg) |
| Double progression simple | applyRangeProgression, cloneSetsFromPastSex (+2,5 kg quand repsMax est atteint, hors Lifting) |
| Mode avant le démarrage d'un cycle | isBeforeForceCycleStart, getBaseModePrescription, forceCycleStartDate sur l'exercice |
| Test de 1RM | buildCycleTestForm, OvrykDB.submitNewOneRM (tire immédiatement le prochain cycle) |
| Alerte de test | renderCycleAlertBanner |
| Calculateur de disques | BAR_WEIGHT_KG (20, constant), settings.plateSet, computePlateLoad, buildPlateCalcPanel |
| Minuteur de repos | startRestTimer, finishRestTimer, formatRestPickerLabel |
| Séries par groupe musculaire | computeWeeklySeriesCounts, PROGRESSION_GROUPS, DEFAULT_TARGETS, ensureMuscleGroupTargets |
| Historique d'un exercice | getExerciseSessionRecords, buildHistoryRow, openExerciseDetail |
| Détection de stagnation | detectStagnation |
| Export et import | collectAllOvrykData, downloadOvrykExport |
| Rappels | ensureNotificationPrefs, renderProfileNotificationsCard |

## Ce qui manque

* Aucune notion de jour de la semaine pour une routine : l'accueil propose la routine la moins récente (computeNextRoutine).
* Pas de réussi ou raté par rep, pas de cause d'échec, pas de compteur de reps pour les séries longues.
* Pas de séparation en blocs dans une séance, pas de séparateur.
* Pas de liste globale des séances (l'historique n'existe que par exercice).
* Pas de volume par jour, pas d'alerte de chevauchement musculaire, pas de décharge de la muscu.
* Pas de coordination des cycles entre mouvements (le décalage par date existe, mais sans règle).
* Le prochain cycle est tiré automatiquement à la validation du 1RM, sans écran de fin de cycle.
* La barre est fixée à 20 kg dans le code.
* Pas de compte ni de sauvegarde en ligne.
* Pas d'import depuis une autre application.
