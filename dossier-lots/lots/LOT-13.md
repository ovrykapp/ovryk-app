# LOT 13. Charge de la semaine et décharge de la muscu

Taille : M. Dépend de : 08, 09.

## Écrans de la maquette

* ../maquette/28-charge-de-la-semaine.png

## Objectif

Afficher la charge de la semaine (par jour, par groupe musculaire), avertir quand deux séances sollicitent la même zone, et alléger la muscu pendant les semaines allégées des cycles.

## Existant à connaître

* computeWeeklySeriesCounts (séries terminées par groupe et par semaine), PROGRESSION_GROUPS, DEFAULT_TARGETS, ensureMuscleGroupTargets, getProgressionGroup, JAMBES_GROUP_MAP.
* Les semaines allégées sont seulement visibles dans le nom de la phase ("Allégée ...").

## À faire

1. Ajouter un drapeau deload aux semaines de cycle : dans mkWeek, option deload ; l'activer sur toutes les semaines dont la phase commence par "Allégée" (cycles 2 à 12).
2. Écran "Charge de la semaine" (maquette 28) : bandeau "À surveiller" si un chevauchement existe (R9), histogramme des séries par jour (haltérophilie en bleu, muscu en orange), barres de séries par groupe musculaire avec l'étiquette "Élevé" au dessus de 1,3 fois l'objectif hebdomadaire.
3. Table des zones sollicitées par exercice, par exemple bas du dos : soulevés de terre, rowing barre, extensions lombaires, tirages et épaulés lourds. Une table dans le code, modifiable.
4. Alerte de chevauchement : R9. Boutons "Déplacer une séance" (change le jour de la routine, lot 02) et "Je garde" (masque l'alerte cette semaine).
5. Branchement : l'alerte alimente le bandeau "À surveiller" de l'écran Programme (lot 02).
6. Décharge de la muscu (R8) : à la construction d'une séance (buildSessionFromRoutine), si le réglage est actif et si au moins un cycle actif est en semaine allégée, retirer un tiers des séries de muscu (minimum 2). Marquer sex.deload et afficher "Séance allégée" avec un bouton "Ignorer".
7. Interrupteur "Alléger aussi la muscu" dans les réglages (lot 14) et par exercice (lot 09).

## Données

week.deload dans FORCE_CYCLES, sex.deload, settings.deloadMuscuMode ('off', 'auto', 'manual' ; remplace le booléen settings.deloadMuscu, jamais créé, décision du 2026-10-10).

## Règles métier concernées

R8, R9.

## Critères d'acceptation

* En semaine allégée d'un cycle, une routine de muscu de six exercices à trois séries ne propose plus que deux séries par exercice.
* "Ignorer" restaure les séries d'origine.
* Un chevauchement de bas du dos mardi et jeudi déclenche l'alerte, pas lundi et jeudi.
* Les barres par groupe correspondent à computeWeeklySeriesCounts.

## Risques

* Le seuil de 1,3 fois l'objectif et la table des zones sont des repères à ajuster à l'usage.
* L'allègement ne doit jamais supprimer une série déjà validée.

## Hors lot

Un coefficient de fatigue différent par mouvement.

## Prompt pour Claude Code

Copie ce texte dans Claude Code, à la racine du projet, après avoir exporté tes données et fait un commit :

> Lis CLAUDE.md et les documents du dossier dossier-lots : METHODE.md, ETAT-DES-LIEUX.md, MODELE-DE-DONNEES.md, REGLES-METIER.md, puis lots/LOT-13.md et les images de maquette citées. Travaille uniquement sur le lot 13. Commence par me proposer un plan des modifications, sans écrire de code, en citant les fonctions et les identifiants que tu comptes toucher. Attends ma validation. Ensuite modifie index.html par petites étapes, vérifie la syntaxe du script, lance node outils/verifier-cycles.js, teste dans un navigateur à 390 x 844 et passe les critères d'acceptation un par un. Ne touche à rien d'autre. Si une règle est ambiguë, pose moi la question.

## Plan détaillé (validé le 2026-10-10)

Décisions du 2026-10-10 :
* Progression automatique figée après une séance allégée : oui.
* Chevauchement à 2 jours calendaires d'écart ou moins : oui.
* Décharge de la muscu : le booléen settings.deloadMuscu est remplacé par settings.deloadMuscuMode à trois valeurs ('off', 'auto', 'manual'), absent = 'off', y compris pour les données existantes (la question 1 sur la valeur par défaut est donc tranchée : désactivée). Voir le point 3 et la livraison 3.
* L'interrupteur par exercice (exercise.deloadMuscu, ancienne livraison 4) est retiré du plan.
* Périmètre immédiat : livraisons 1 et 2. La livraison 3 reste à faire, sur une nouvelle demande.

Lot à risque (cycles, construction des séances, réglages, écriture dans routine.weekdays). Un seul plan, validation, puis les quatre livraisons enchaînées, un commit et une version de sw.js chacune.

### 1. Écran "Charge de la semaine" (390 px)

Page plein écran (comme cycle-detail-page), ouverte depuis l'écran Programme (ligne "Charge de la semaine" sous le planning de la semaine) et depuis le bandeau "À surveiller" du Programme. Titre, sous-titre "Semaine du 5 octobre" (lundi de la semaine civile, weekKeyOf).

1. Bandeau "À surveiller" (seulement s'il y a un chevauchement non masqué) : une phrase par chevauchement, réelle ("Le soulevé de terre roumain de mardi et le rowing barre de jeudi sollicitent tous les deux le bas du dos, à 2 jours d'écart."), boutons "Déplacer une séance" et "Je garde". S'il y en a plusieurs : le premier en clair, les suivants repliés sous "2 autres".
2. Séries par jour : histogramme lundi à dimanche, deux couleurs (haltérophilie bleu, muscu orange, variables existantes). Jour passé ou aujourd'hui : séries validées (done) des séances de ce jour. Jour à venir : séries prévues des routines placées ce jour (routine.weekdays), barres en contour pour les distinguer du réalisé. Une semaine allégée est reflétée dans le prévu (même fonction que la séance).
3. Séries par groupe musculaire : une barre par groupe de PROGRESSION_GROUPS, valeur = computeWeeklySeriesCounts()[groupe][semaine courante] (validé seulement, comme le critère d'acceptation), objectif getMuscleGroupTargets, étiquette "Élevé" au dessus de 1,3 fois l'objectif. Groupes à 0 repliés sous "Afficher tous les groupes".
4. Note de bas : "Un groupe est signalé Élevé au dessus de 1,3 fois son objectif. Repère à ajuster."

Tout est calculé à l'affichage. Seuls stockés : le masquage "Je garde" (voir livraison 2) et, si "Déplacer une séance" est validé, routine.weekdays (champ existant, même chemin d'écriture que le sélecteur de jours). Aucune écriture à l'ouverture.

Table des zones (code, modifiable) : MUSCLE_ZONES = { bas_du_dos, jambes, epaules }, chaque zone liste des motifs de nom d'exercice (soulevé de terre, roumain, rowing barre, extension lombaire, tirage, épaulé, clean, snatch, arraché, squat, fente, presse, développé militaire, push press, jerk...) et des identifiants d'exercices de base. Un exercice personnalisé est rattaché par son nom ; sans correspondance, aucune zone.

Chevauchement (R9) : pour chaque paire de séances de la semaine (réalisées ou prévues) dont l'écart est de 2 jours calendaires ou moins, et pour chaque zone, si chacune des deux séances y compte au moins 3 séries, alerte. Mardi et jeudi : alerte ; lundi et jeudi : non (critère d'acceptation, décision du 2026-10-10).

### 2. Semaine allégée : détection et séance de muscu

Drapeau : mkWeek reçoit l'option deload ; { deload: true } posé sur les 11 semaines dont la phase commence par "Allégée" (cycles 2 à 12 ; ni le cycle 1 ni A à E n'en ont). getCycleWeekAt recopie deload quand une semaine est modifiée (semaines_modifiees), sinon le drapeau serait perdu. verifier-cycles.js contrôle "phase Allégée si et seulement si deload". docs/CYCLES.md et data/cycles_generiques.json régénérés. Rien de stocké : FORCE_CYCLES est dans le code.

Détection, nouvelle fonction pure getDeloadCyclesForWeek(dateRef) : pour chaque cycle de force, ignorer en_attente_de_validation et isBeforeForceCycleStart ; semaine retenue = celle réellement jouée cette semaine civile si une séance terminée de ce mouvement existe déjà (resolveLightSessionWeekNumber, comme R12), sinon cycle.semaine_actuelle. Raison : semaine_actuelle avance dès la séance d'haltérophilie terminée ; sans cette règle, la muscu du lendemain ne serait plus allégée alors que la semaine civile l'est. Résultat : liste { exerciseId, cycleId, weekNumber }.

Construction (buildSessionFromRoutine, seul constructeur depuis une routine) : la séance est d'abord construite exactement comme aujourd'hui, puis une étape applyMuscuDeload(session) s'applique si settings.deloadMuscuMode vaut 'auto' et si la liste ci-dessus n'est pas vide (en mode 'manual', la même fonction est appelée par le bouton "Alléger cette séance", voir le point 3). Pour chaque exercice de séance de type muscu (getExerciseType === 'muscu', jamais un mouvement de cycle, jamais le mode de base, jamais une séance légère R12) :
* séries gardées = max(min(n, 2), n - arrondi(n / 3)) : 3 donne 2, 4 donne 3, 5 donne 3, 6 donne 4, 2 et 1 inchangés ;
* les dernières séries sont retirées ; charge et reps inchangées (celles de la double progression ou de la routine).

Stocké sur l'exercice de séance (champs nouveaux, optionnels) : deload: true, deloadRemovedSets (les séries retirées, intactes, done à false), deloadSource ({ exerciseId, cycleId, weekNumber } du premier cycle allégé, pour le texte). Un exercice qui n'est pas allégé ne reçoit aucun champ. Recalculé à l'affichage : le texte du bandeau "Séance allégée : semaine allégée du Cycle 7 (Arraché). Muscu : un tiers des séries en moins, charges inchangées." et son bouton "Ignorer".

"Ignorer" (un geste, toute la séance) : chaque exercice allégé récupère ses deloadRemovedSets en fin de liste, deload passe à false, deloadIgnored: true, deloadRemovedSets: null. Rien n'est jamais retiré à ce moment, donc aucune série validée ne peut disparaître. L'allègement ne se fait qu'à la construction, quand aucune série n'est validée.

Non allégés : séance vide (buildEmptySession), exercice ajouté en cours de séance (doAddExerciseToSession), séance déjà en cours au moment de la mise à jour.

### 3. Réglage settings.deloadMuscuMode (livraison 3, redéfini le 2026-10-10, non codé)

* Trois valeurs : 'off' (décharge désactivée), 'auto' (suit les semaines allégées des cycles, point 2), 'manual' (l'utilisateur l'applique lui-même). Champ absent = 'off', y compris pour les données existantes. Lecture seule de la valeur par une fonction getDeloadMuscuMode() qui renvoie 'off' pour toute valeur absente ou inconnue ; aucune écriture par migrateSchema (absent vaut déjà 'off'). DEFAULT_SETTINGS ne reçoit pas de valeur, ou 'off'.
* Le booléen settings.deloadMuscu prévu par MODELE-DE-DONNEES.md n'est jamais créé.
* Réglages : une ligne "Décharge de la muscu" à trois choix (Désactivée, Suit les cycles, Manuelle), affichée seulement s'il existe au moins un cycle d'haltérophilie actif (cycle de force présent, pas en_attente_de_validation, exercice existant). Sans cycle actif, la ligne est masquée (jamais de réglage sans effet) et la valeur déjà enregistrée est conservée telle quelle, jamais remise à 'off'. Écrit seulement au changement de choix.
* 'off' : rien ne change par rapport à aujourd'hui. applyMuscuDeload n'est jamais appelé, aucun bouton n'apparaît, aucun champ deload n'est posé.
* 'auto' : allègement à la construction de la séance (point 2), bandeau "Séance allégée" et "Ignorer".
* 'manual' : aucune détection automatique. Dans une séance en cours qui contient au moins un exercice de muscu allégeable (au moins 3 séries, aucune série validée sur les séries à retirer), un bouton "Alléger cette séance" applique le même allègement que le mode auto : retire les dernières séries non validées, stocke deload: true et deloadRemovedSets, deloadSource: 'manual'. "Ignorer" les remet, comme en mode auto. Le bouton n'écrit qu'au clic. Une série validée n'est jamais retirée : seules les dernières séries non validées peuvent l'être, et un exercice dont il faudrait retirer une série validée garde ses séries.
* Effet testable dès la livraison 3 : en 'auto', semaine allégée active, routine de muscu à 3 séries, la séance propose 2 séries ; en 'manual', 3 séries puis 2 après le bouton ; en 'off', 3 et aucun bouton.

### 4. Données existantes et lecteurs

Aucune séance passée, aucune séance en cours, aucune routine n'est modifiée ni recalculée : l'allègement agit sur la copie construite pour une nouvelle séance. Une séance sans champ deload se lit comme aujourd'hui.

| Lecteur | Séance allégée comptée normalement ? | Pourquoi |
|---|---|---|
| Volume (computeWeeklySeriesCounts, résumé de la semaine, Charge de la semaine) | Oui | Ce sont des séries réellement faites, le volume doit montrer la baisse. |
| Records, meilleur, 1RM estimé (getExerciseSessionRecords, getBestRecordForExercise) | Oui | Charge inchangée, reps réelles : un record fait en séance allégée est un vrai record. |
| R5, progression (cloneSetsFromPastSex, computeRangeProgressionDecision) | Non | Voir point 5 (décision du 2026-10-10 : progression figée). |
| R5, baisse suggérée (checkDeloadSuggestion) | Non | Deux séances de suite sous la plage : une séance allégée est sautée, on regarde les précédentes. |
| Stagnation (detectStagnation) | Non | Moins de séries donne moins de reps totales : fausse stagnation. Séance allégée sautée. |
| Historique et détail | Oui, avec l'étiquette "Allégée" | Affichage seul. |
| Progrès | Oui | Mêmes données que le volume. |
| Stats de fin de cycle (computeCycleStats) | Non concerné | Ne lit que les mouvements de cycle, jamais allégés. |

### 5. Interactions

* R5 : la séance suivant une séance allégée repart de deloadRemovedSets ajoutées à ses séries, donc du nombre de séries d'origine. La séance allégée ne sert jamais de référence de progression : charge et reps cibles reprises telles quelles (pas de montée, pas de remise de targetReps au bas de plage). Après "Ignorer", la séance est normale et compte normalement.
* R7 : isHeavyWeek et la coordination ne changent pas (le cycle 2 semaine 7, Allégée à 85 %, reste compté lourd). Dans la grille, la priorité devient Test, puis Pic, puis Allégée (aujourd'hui Allégée passe avant), pour que l'étiquette reste cohérente avec le décompte ; la légende "Allégée" apparaît.
* R12 : seuls les mouvements de cycle ont une séance légère, la muscu n'est jamais concernée ; une semaine allégée vue depuis une deuxième séance est lue sur la semaine réellement jouée (même fonction).
* Popup de semaine de test : elle s'exécute avant buildSessionFromRoutine ; la détection voit l'état après le choix (Repousser, Changer de cycle). Une semaine de test n'est jamais allégée.

### 6. Risques et endroits du code

Risques : séries recopiées en moins à la séance suivante (traité au point 5) ; cycle dont semaine_actuelle n'avance pas (pas d'haltérophilie pendant deux semaines) qui garde la muscu allégée plusieurs semaines : comportement de R8 tel qu'écrit, signalé par le bandeau ; drapeau perdu sur une semaine modifiée (getCycleWeekAt) ; table des zones approximative pour les exercices personnalisés ; "Déplacer une séance" écrit routine.weekdays (même chemin et même format que le sélecteur de jours).

Lecteurs de week.deload aujourd'hui : un seul, la grille de coordination (renderCoordinationTable, cellule is-allegee) et sa légende qui l'exclut volontairement. Après le lot : cette grille, getDeloadCyclesForWeek, verifier-cycles.js et les deux générateurs. getCycleWeekAt doit transmettre le champ.

Construction d'une séance à partir d'une routine : buildSessionFromRoutine uniquement, appelé par launchRoutineSession, lui-même appelé par la carte de routine du Programme, le panneau du jour (buildProgrammeDayPanelCard), la liste de l'onglet Séance (renderSeanceRoutineList), "Refaire cette séance" (renderHistoryDetailFooter) et l'Accueil. Construisent aussi des séries sans routine : doAddExerciseToSession (buildCycleSessionSets), buildEmptySession, non allégés. Sous-fonctions touchées : cloneSetsFromPastSex, cloneSetsFromRoutineRex (inchangée), buildCycleSessionSets (inchangée).

### 7. Livraisons

1. Lecture seule : drapeau deload dans FORCE_CYCLES, getCycleWeekAt, verifier-cycles.js, documents régénérés, grille de coordination ; écran Charge de la semaine (jours, groupes, chevauchements affichés sans bouton) ; table des zones. Aucune écriture. Interface pure dans son effet, mais touche aux cycles : traitée à risque.
2. Actions de l'alerte : "Je garde" (nouveau champ optionnel settings.chargeAlertesMasquees, { semaine: [clés d'alerte] }, écrit au clic, purgé des semaines passées au même moment), "Déplacer une séance" (ouvre le sélecteur de jours existant de la routine concernée), bandeau "À surveiller" sur le Programme. À risque (écriture dans les routines).
3. Réglage et allègement ensemble (redéfinie le 2026-10-10, non codée) : settings.deloadMuscuMode ('off', 'auto', 'manual', absent = 'off'), ligne à trois choix dans Réglages affichée seulement avec au moins un cycle d'haltérophilie actif, applyMuscuDeload, sex.deload, deloadRemovedSets, deloadSource, bandeau "Séance allégée" et "Ignorer" (mode auto), bouton "Alléger cette séance" (mode manuel), lecteurs R5 (progression figée), baisse suggérée et stagnation, étiquette dans l'Historique. Le réglage n'arrive pas avant l'allègement : il serait sans effet. À risque.
4. Supprimée le 2026-10-10 : plus d'interrupteur par exercice (exercise.deloadMuscu n'est pas créé).

Tests de chaque livraison : node --check, verifier-cycles.js, smoke.py, puis import de backups/ovryk-export-2026-10-01.json sur la copie locale : export avant et après identiques hors nouveaux champs, séances et routines inchangées.

## Avancement

* Livraison 1 faite le 2026-10-10 (sw v118) : drapeau deload sur les 11 semaines "Allégée" (mkWeek, option deload), recopié par getCycleWeekAt pour une semaine modifiée ; verifier-cycles.js contrôle "phase Allégée si et seulement si deload" et "jamais allégée et test" ; data/cycles_generiques.json régénéré (docs/CYCLES.md inchangé, il n'affiche pas le drapeau). Grille de coordination : Test, puis Pic, puis Allégée, légende "Allégée (A)". Écran "Charge de la semaine" (page week-load-page, renderWeekLoadPage) ouvert depuis une carte en bas du Programme (programme-week-load-btn) : bandeau "À surveiller" sans bouton, séries par jour (validées, ou prévues en pointillés pour aujourd'hui sans séance et les jours à venir), séries par groupe (computeWeeklySeriesCounts, "Élevé" au dessus de 1,3 fois l'objectif). Table MUSCLE_ZONES (bas du dos, jambes, épaules), computeWeekOverlaps. Rien n'est stocké, aucune écriture à l'ouverture (vérifié en comparant tout le localStorage avant et après).
* Livraison 2 faite le 2026-10-10 (sw v119) : chaque alerte a ses boutons. "Je garde" écrit settings.chargeAlertesMasquees ({ clé de semaine weekKeyOf: [clés zone|jour|jour] }), seulement au clic, en ne gardant que la semaine en cours. "Déplacer une séance" n'apparaît que si une routine de l'alerte est placée ce jour là (une séance libre ne se déplace pas) ; il ouvre une feuille (séance à déplacer s'il y en a deux, puis nouveau jour, jours déjà prévus grisés), puis une confirmation qui rappelle les jours avant et après. Seul routine.weekdays est écrit, sur confirmation, sans OvrykDB.updateRoutine : updatedAt ne bouge pas, la séance suivante de la routine reprend toujours la dernière séance (R5). Aucune séance enregistrée ni en cours n'est touchée. Le Programme affiche la carte en mode "À surveiller" (première alerte non masquée, nombre des autres) quand une alerte est visible, sinon "Charge de la semaine".
* Livraison 3 en attente (réglage deloadMuscuMode, bouton manuel, allègement), à lancer sur une nouvelle demande.
* Correction après audit le 2026-10-10 (sw v120) : une routine = une seule occurrence dans la charge (faite si elle existe, sinon prévue, même à un autre jour) ; une séance prévue aujourd'hui n'est plus masquée par une autre séance du même jour (deux routines différentes comptent toutes les deux) ; la légende "Allégée (A)" de la Coordination n'apparaît que si une case A est affichée ; code mort retiré (champ alerts du résumé, label des entrées, deux règles de style).
* A surveiller à la livraison 3 : getPlannedSetCount recopie le choix cycle, mode de base ou routine de buildSessionFromRoutine pour compter les séries prévues. Quand buildSessionFromRoutine saura alléger la muscu (mode auto), getPlannedSetCount doit évoluer avec lui (séries prévues allégées), sinon la charge prévue affichée ne correspondra plus à la séance construite. Idéalement, factoriser le calcul du nombre de séries dans une fonction partagée.
