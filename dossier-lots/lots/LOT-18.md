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
2. En cas de doublon, le "dernière séance" d'une carte de remplacement aurait été pris sur la première carte Y de la séance. Limite levée par la règle du créneau (findSexForSlot, livraison 2) : chaque carte a son propre "dernière séance".

## Livraisons

1. Modèle et éditeur d'équivalent, sans changement des séances (sw v139).
2. Pilule sur l'écran de départ, remplacement à la construction, salle enregistrée et affichée, règles du doublon, allègement automatique (lot 13) vérifié et réglé sur une carte remplacée (sw v140).
3. Changement de salle pendant la séance avant la première série (reconstruction ciblée), verrouillage (sw v141).

## Avancement

* Livraison 1 faite le 2026-10-15 (sw v139), en local, non poussée.
  * Fiche exercice (renderExerciseDetailFicheExtra) : ligne "Équivalent en salle indé · nom" (ou "Aucun", ou "Équivalent introuvable"), absente pour un mouvement (Lifting). La fiche de la cible indique "Fait en salle indé à la place de : …".
  * Écran exercise-equiv-page : recherche (normalizeSearch existante), "Aucun équivalent" en tête, choix non disponibles grisés avec leur raison, sélection en orange. Rien n'est écrit avant "Enregistrer" ; "Aucun" sur un exercice qui n'a jamais eu d'équivalent n'écrit rien.
  * OvrykDB.updateExerciseGymEquivalent : n'écrit que l'exercice concerné. Fonctions getGymEquivalent, getGymEquivalentSources, getGymEquivalentError.
  * Aucune séance n'est modifiée : une routine se lance toujours avec l'exercice d'origine, sans salle.
  * Tests : dossier-lots/tests/test_gym.py (19 contrôles, données fabriquées).

## Hors périmètre

Bouton Reps/Plage, flèches de l'éditeur, écran du repos par type, gardes de lecture, suite de tests de la restauration locale, migration des routines "(indé)".
