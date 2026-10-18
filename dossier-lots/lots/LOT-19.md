# LOT 19. Machine à On Air par créneau de routine

Statut (2026-10-18) : livraisons 1 (sw v157) et 2 (sw v158) faites en local, non poussées, à auditer chacune par Opus. Un seul push après l'audit Opus de la livraison 2, sur accord explicite de Ruben.

Lot à risque (écriture dans des routines existantes, puis construction des séances). Plan approuvé par Ruben le 2026-10-18 (plan dans ~/.claude/plans).

## Objectif

Le programme principal de Ruben est en salle indé : ses routines portent l'exercice fait en indé. Il choisit, dans l'éditeur, par créneau de routine, la machine à faire à On Air à la place. Facultatif : absent = comportement actuel (lot 18 inchangé pour tous les créneaux existants, routines « (indé) » comprises). Aucune migration.

## Modèle de données

* rex.onairExerciseId : chaîne, null (choix retiré) ou absent (jamais défini). Écrit seulement depuis les réglages du créneau (OvrykDB.updateRoutineSlotOnAir), qui relit la routine au moment d'écrire, n'écrit que ce champ et ne touche jamais routine.updatedAt (décision de Ruben, comme les jours).
* Aucune clé nouvelle, schemaVersion 2, migrateSchema inchangé. Export, import, restauration : le champ suit les données telles quelles.

## Règles

* Choix valide : la machine existe, n'est pas l'exercice du créneau, ni elle ni l'exercice du créneau ne sont des mouvements (Lifting), le créneau n'a pas de cycle. Un seul saut.
* Le créneau gagne sur la fiche exercice : un créneau avec une machine On Air valide est fait tel quel en indé (l'équivalent indé de la fiche est ignoré pour ce créneau) et remplacé par la machine à On Air (livraison 2).
* L'historique, la progression et le 1RM appartiennent toujours à l'exercice réellement fait (carte : exerciseId = exercice fait, replacesExerciseId = exercice du créneau, comme le lot 18).
* Machine introuvable (seulement après la restauration d'un fichier incohérent : l'app ne permet pas de supprimer un exercice) : affichée « Machine introuvable », le créneau se comporte comme sans choix, le champ est conservé sans écriture.
* Pas de création d'exercice depuis l'écran de choix (décision de Ruben) : exercices existants seulement.

## Livraisons

1. Mémorisation et éditeur, aucune séance touchée (sw v157).
2. Comportement en séance : getRoutineSlotReplacement généralisé, isGymLinkedExercise étendu, changement de salle dans les deux sens, libellés (sw v158).

## Avancement

* Livraison 1 faite le 2026-10-18 (sw v157), en local.
  * OvrykDB.updateRoutineSlotOnAir ; duplicateRoutine copie onairExerciseId (il reconstruisait chaque ligne champ par champ et l'aurait perdu).
  * Réglages du créneau : section « Machine à On Air · … » (absente pour un mouvement Lifting, inaccessible de toute façon : ses réglages ne s'ouvrent pas) ; écran routine-onair-page (recherche, « Aucune machine » en tête, non disponibles grisés avec leur raison, contrôle refait à l'écriture, rien écrit avant Enregistrer, « Aucune » sur un créneau sans choix n'écrit rien) ; résumé du créneau dans l'éditeur « · On Air : Nom ».
  * Règle 14 : après l'écriture, le rex de même identifiant de routineEditorLive reçoit le champ en place (sécurité en plus : la fermeture des réglages redessine déjà l'éditeur depuis le stockage).
  * Conservation du champ vérifiée par chemin : nom, jours, monter, descendre, grouper, type, dissoudre, kilos, repos, ajout, retrait d'un autre créneau, Enregistrer, duplication, remplacement de la 3a (copie toutes les clés), export et restauration, migrateSchema. Glisser-déposer : non testé (réinsère le même objet, lu dans le code).
  * Tests : dossier-lots/tests/test_onair.py (41 contrôles). Mutations : duplication sans le champ, updatedAt touché, Lifting proposé, contrôle non refait à l'écriture, écriture sans choix : détectées ; section pour un Lifting et copie de l'éditeur non synchronisée : non détectées (chemin inaccessible, sécurité redondante).
* Livraison 2 faite le 2026-10-18 (sw v158), en local.
  * getRoutineSlotReplacement(rex, gym) : machine On Air valide -> remplace le créneau à On Air, créneau fait tel quel en indé (il gagne sur l'équivalent de la fiche) ; sinon lot 18 inchangé.
  * isGymLinkedExercise étendu (isRoutineSlotOnAirLinked) : la reprise de la machine et de l'exercice du créneau lit la dernière séance de la routine avec ce créneau, pas la dernière séance de la routine (faite dans l'autre salle).
  * buildGymSwitchedExercises : la n-ième ligne d'un exercice correspond à la n-ième carte de ce créneau (normale ou qui le remplace) ; une carte n'est reconstruite que si l'exercice voulu pour la nouvelle salle diffère. Sans machine On Air, résultat identique au lot 18 (test_gym 77/77 inchangé).
  * Libellés : « N remplacé(s) à On Air » ou « en indé » selon la salle ; « Remplace X (On Air) » ou « (salle indé) » sur la carte et dans l'historique.
  * Tests : test_onair.py, 60 contrôles (S1 à S9 ajoutés ; le contrôle O7 de la livraison 1, « séances inchangées », remplacé par S1 à S4). Mutations : créneau qui ne gagne plus en indé, machine ignorée, sens inversé, reprise non étendue, changement de salle à sens unique : détectées ; garde du cycle retirée de getRoutineSlotReplacement : non détectée (redondante avec getRoutineSlotOnAirError, seul un Lifting peut avoir un cycle).
  * Limite héritée du lot 18 (limite 3) : une machine sans historique dans le créneau part de la charge d'une carte normale de la machine dans la routine, sinon de charges vides.
