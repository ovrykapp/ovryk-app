# LOT 14. Réglages et matériel

Taille : M. Dépend de : 01. Lot à risque (réglages lus par les séances, R2, R5, R10) : un seul plan, approbation, puis toutes les livraisons à la suite. Cadrage du 2026-10-10 ci-dessous, trois décisions en attente.

## Écrans de la maquette

* ../maquette/16-reglages.png
* ../maquette/17-barre-et-disques.png

## Objectif

Refaire l'écran Réglages et rendre le matériel configurable.

## Existant à connaître

* Section view-profil : objectifs hebdomadaires (renderProfileGoalsCard), notifications (renderProfileNotificationsCard, ensureNotificationPrefs), sauvegarde (collectAllOvrykData, downloadOvrykExport, import), réinitialisation.
* La barre est une constante : BAR_WEIGHT_KG = 20. Les disques sont dans settings.plateSet (ensurePlateSet, savePlateSet).

## À faire

1. Réglages (maquette 16), par blocs : Progression automatique (pas de montée et plage de reps par défaut, alerte RPE), Repos automatique (trois durées par type), Général (barre et disques, rappels, unité), Données (compte, importer, exporter, réinitialiser).
2. Conserver les objectifs hebdomadaires et les notifications existants dans cet écran.
3. Écran "Barre et disques" (maquette 17) : poids de la barre (15, 20 ou autre) qui remplace la constante BAR_WEIGHT_KG par settings.barWeightKg partout, choix des disques disponibles, aperçu du chargement, et "plus petit saut de charge possible" (deux fois le plus petit disque).
4. Utiliser ce plus petit saut pour que la progression automatique et computeWeightFromPercent ne proposent jamais une charge impossible à monter.
5. Nouveaux réglages de MODELE-DE-DONNEES.md avec leurs valeurs par défaut, branchés dans les lots précédents.
6. Garder l'avertissement de sauvegarde (renderBackupReminder).

## Données

settings.barWeightKg, defaultProgressionStep, defaultRepRange, restByType, deloadMuscu.

## Règles métier concernées

R2, R5, R10.

## Critères d'acceptation

* Changer la barre à 15 kg change tous les calculs de chargement.
* Retirer un disque de 1,25 change le plus petit saut possible et les charges proposées.
* Les durées de repos par type sont appliquées aux nouvelles séances.
* Les objectifs hebdomadaires et les notifications fonctionnent comme avant.

## Risques

* Changer l'arrondi de computeWeightFromPercent modifie les charges de toutes les séances futures : ne le faire que depuis le plus petit saut configuré, et jamais pour les séances passées (charges figées).

## Hors lot

Unité en livres, compte (lot 16).

## Cadrage (2026-10-10)

### 1. Écran Réglages (view-profil)

Aujourd'hui : quatre blocs à plat (Objectifs hebdomadaires avec 9 compteurs, Notifications, Sauvegarde, Réinitialisation). Proposé, à 390 px, en sections comme la maquette 16 :

* Progression automatique : "Palier de montée par défaut" (2,5 kg, feuille de choix 1, 1,25, 2,5, 5) et "Plage de reps par défaut" (8 à 10, feuille avec bas et haut). Lisent et écrivent settings.defaultProgressionStep et settings.defaultRepRange, champs existants. Portée : décision 3.
* Repos automatique : livraison séparée (décision 2). Trois lignes "Mouvement technique", "Force en pourcentage", "Accessoire et muscu", avec la feuille de repos existante (rest-picker).
* Général : "Barre et disques" (résumé "Barre de 20 kg", ouvre la page de la maquette 17), puis les trois notifications existantes (Rappel de séance, Repos terminé, Résumé hebdomadaire), inchangées.
* Objectifs hebdomadaires : une ligne avec résumé, repliée par défaut, qui déplie les 9 compteurs existants (même comportement).
* Données : Exporter, Importer (mêmes fonctions, même fichier JSON), rappel de sauvegarde (renderBackupReminder, gardé), puis Réinitialiser l'app en dernier, toujours avec confirmation.

Pas construits, pour ne créer aucun interrupteur sans effet : "Prévenir si le RPE est trop haut" (RPE retiré, point D.2), "Unité de poids" kg ou lb (hors lot), "Compte et sauvegarde" (lot 16), "Alléger aussi la muscu" (deloadMuscu, lot 13).

Constat à corriger à la livraison 1 : ouvrir Réglages écrit déjà dans les réglages quand une valeur manque (ensureNotificationPrefs, ensureMuscleGroupTargets). Ces écritures ne font que compléter, jamais écraser, mais contredisent "aucune écriture à l'ouverture". L'affichage lira les valeurs par défaut sans écrire ; l'écriture ne se fera qu'au premier changement.

### 2. Barre et disques configurables

Où vit le réglage :

* settings.barWeightKg : absent = 20 (MODELE-DE-DONNEES.md). Lu par getBarWeightKg() (déjà en place depuis le lot 17, livraison 1), qui renverra settings.barWeightKg s'il est un nombre positif, sinon 20.
* settings.plateSet : champ qui existe déjà dans le code. Absent ou vide = DEFAULT_PLATE_SET [25, 20, 15, 10, 5, 2,5, 1,25]. Lu par getPlateSetForDisplay() (lecture seule).
* Aucune migration : rien n'est écrit au chargement. Avec les réglages absents, le comportement est exactement celui d'aujourd'hui (barre de 20 kg, plus petit disque 1,25, plus petit saut 2,5 kg). Écriture seulement au tap sur "Enregistrer" de la page Barre et disques ; quitter sans enregistrer ne change rien.

Page Barre et disques (maquette 17) : barre 15, 20 ou Autre (champ, nombre positif) ; disques à cocher (25, 20, 15, 10, 5, 2,5, 1,25, 0,5, plus tout disque personnalisé déjà présent dans settings.plateSet) ; au moins un disque obligatoire ; aperçu du chargement calculé sur le brouillon ; plus petit saut = deux fois le plus petit disque coché.

Tous les endroits qui lisent la barre ou les disques (relevé du 2026-10-10) :

* getBarWeightKg() : lu par buildBarLoadCard (carte "Chargement par côté" de la séance en cours, muscu sur barre ou sans matériel, et haltérophilie), dans le texte "barre de X kg" et "Barre de X kg seule".
* computePlateLoad(target, plateSet) : lit BAR_WEIGHT_KG en direct. À passer par getBarWeightKg().
* getPlateSetForDisplay() : lu par buildBarLoadCard.
* buildPlateCalcPanel, guessInitialPlateWeight, buildPlateSetEditor, ensurePlateSet, savePlateSet : code du calculateur de disques, appelé nulle part aujourd'hui. Lit BAR_WEIGHT_KG en direct (texte "Poids inférieur ou égal à la barre seule", total) et écrit settings.plateSet via ensurePlateSet. À aligner sur getBarWeightKg() et getPlateSetForDisplay() sans le rebrancher ; pas de suppression (règle 9).
* computeWeightFromPercent : ne lit ni la barre ni les disques. Arrondi fixe au multiple de 2,5 kg (R2). Appelé à 20 endroits : séance en cours (lignes, pastilles de %, réglage de charge, feuille Un raté, taux de réussite), volume (computeSetVolume), historique et records (resolveDoneSets, getHistorySetKg), détail d'un cycle, prescriptions des routines, fiche type d'exercice. C'est le point de la décision 1.
* Pas de barre ni de disques ailleurs : historique, volume, records et résumés de carte n'utilisent que des kilos totaux.

### 3. Séances enregistrées et séance en cours

Ce qui est stocké et ce qui est calculé :

* Muscu : set.weightKg est le poids total stocké (barre comprise ; un haltère pour le matériel Haltères, décision 3A du lot 17). Changer la barre ou les disques ne le modifie jamais. Le "par côté" est calculé à l'affichage, dans la carte de chargement de la séance en cours seulement.
* Haltérophilie : la séance stocke set.percent1rm et sex.oneRepMaxSnapshot ; le poids en kilos est recalculé à chaque affichage par computeWeightFromPercent. La barre n'y entre pas. Les disques n'y entrent pas tant que R2 est inchangé (décision 1).
* Séances passées : aucune écriture, aucun recalcul de données. L'historique, le volume, les records et le taux de réussite restent identiques, car ils ne dépendent ni de la barre ni des disques (sous la décision 1A).
* Séance en cours : aucune série n'est réécrite. Seul le texte "par côté" de la carte de chargement suit le nouveau réglage, avec le même poids total.

### 4. Risques et tests

Risques :

* Changer l'arrondi de computeWeightFromPercent changerait l'affichage des kilos, le volume et les records de toutes les séances d'haltérophilie passées, puisque les kilos n'y sont pas stockés. D'où la décision 1.
* Un plus petit saut plus grand que le palier de montée (par exemple disques sans 1,25, saut de 5 kg, palier de 2,5) : R5 proposerait une charge impossible à monter sur une barre.
* Barre plus lourde que la charge prévue : la carte affiche "Barre de X kg seule", déjà géré (tooLight).
* Réglage absent ou invalide (barre à 0, liste vide) : lecture avec valeur par défaut, et validation à l'enregistrement.

Tests, sur la copie locale avec l'export de backups/ :

* Avant et après l'ouverture de Réglages et de Barre et disques sans enregistrer : toutes les clés ovryk.* identiques.
* Barre à 15 kg enregistrée : seul settings.barWeightKg change, ovryk.sessions identique octet pour octet. Volumes de toutes les séances, records, détail de l'historique et taux de réussite identiques avant et après (comparaison automatique sur les 10 séances de l'export).
* Séance en cours : avant et après le changement, mêmes séries stockées, seul le "par côté" change (60 kg avec une barre de 15 donne 20 + 2,5 par côté).
* Retrait du disque de 1,25 : plus petit saut 5 kg, et la carte signale "il manque 2,5 kg" pour 62,5 kg.
* Export, import, export : fichiers identiques, settings.barWeightKg et settings.plateSet conservés.
* Contrôles habituels : node --check, verifier-cycles.js, smoke.py, 390 x 844.

### 5. Repos par type (settings.restByType)

Livraison séparée (livraison 5 ci-dessous), selon la décision 2. Aujourd'hui, seul addExercisesToRoutine le lit, comme repos par défaut d'un exercice ajouté à une routine ; une séance prend toujours le repos de la routine (rex.restSeconds) ou de la semaine de cycle (R10). Pas d'interrupteur deloadMuscu (lot 13).

### 6. Livraisons

1. Réglages restructuré : sections, Objectifs hebdomadaires repliés, Données, notifications existantes ; lecture des valeurs par défaut sans écriture à l'ouverture. Interface seule.
2. Palier de montée et plage de reps par défaut éditables (settings.defaultProgressionStep, settings.defaultRepRange), portée selon la décision 3. À risque (R5, réglages lus à la création d'exercices et de séries).
3. Page Barre et disques : settings.barWeightKg et settings.plateSet, Enregistrer, getBarWeightKg et computePlateLoad branchés sur le réglage, calculateur non utilisé aligné, "il manque X kg" dans la carte de chargement. À risque (réglage lu par la séance en cours).
4. Plus petit saut de charge appliqué, selon la décision 1. À risque (R2, R5).
5. Repos automatique par type, si la décision 2 le retient. À risque léger (réglage lu à l'ajout d'exercices, ou aux nouvelles séances selon la décision).

### 7. Décisions à prendre par Ruben

1. Plus petit saut de charge et arrondi des charges (R2) :
   A. L'arrondi de computeWeightFromPercent reste à 2,5 kg partout. Le plus petit saut sert à l'affichage (écran Barre et disques, "il manque X kg" dans la carte de chargement) et, sur les exercices à la barre seulement, empêche R5 de proposer une montée plus petite que lui. Aucune séance passée ne bouge (recommandé).
   B. Les nouvelles séances arrondissent au plus petit saut. Il faut alors figer ce saut dans chaque nouvel exercice de séance (nouveau champ optionnel, absent = 2,5), pour que les séances passées restent à 2,5. Les prescriptions des cycles changent (par exemple 71 kg au lieu de 72,5 avec un saut de 1 kg).
2. Repos automatique par type (settings.restByType) :
   A. Livraison 5 : les trois durées réglables changent le repos par défaut d'un exercice ajouté ensuite à une routine, sans toucher aux routines existantes (recommandé).
   B. Comme A, et en plus les nouvelles séances prennent ce repos à la place de celui réglé dans la routine. Le critère du lot le dit, mais cela écrase le repos choisi exercice par exercice.
   C. Pas dans ce lot.
3. Palier de montée et plage de reps par défaut :
   A. Le changement ne vaut que pour les exercices et les séries créés ensuite. Les exercices existants gardent leur palier (migrateSchema a déjà copié 2,5 dans chacun) et les routines leur plage (recommandé).
   B. Comme A, avec en plus un bouton "Appliquer à tous les exercices" qui réécrit le palier des exercices encore à l'ancienne valeur. C'est une écriture dans des données existantes.

## Prompt pour Claude Code

Copie ce texte dans Claude Code, à la racine du projet, après avoir exporté tes données et fait un commit :

> Lis CLAUDE.md et les documents du dossier dossier-lots : METHODE.md, ETAT-DES-LIEUX.md, MODELE-DE-DONNEES.md, REGLES-METIER.md, puis lots/LOT-14.md et les images de maquette citées. Travaille uniquement sur le lot 14. Commence par me proposer un plan des modifications, sans écrire de code, en citant les fonctions et les identifiants que tu comptes toucher. Attends ma validation. Ensuite modifie index.html par petites étapes, vérifie la syntaxe du script, lance node outils/verifier-cycles.js, teste dans un navigateur à 390 x 844 et passe les critères d'acceptation un par un. Ne touche à rien d'autre. Si une règle est ambiguë, pose moi la question.
