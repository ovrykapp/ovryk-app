# Modèle de données : ajouts et migration

Tous les ajouts sont optionnels et ont une valeur par défaut : un export ancien doit continuer à s'importer sans erreur.

## Version de schéma

Ajouter une clé ovryk.meta avec { schemaVersion: 2 }. Écrire une fonction migrateSchema(), idempotente, appelée à l'initialisation, qui complète les champs manquants. Elle ne supprime jamais rien.

## Ajouts par entité

### Routine
* weekdays : tableau de nombres de 1 (lundi) à 7 (dimanche). Défaut : tableau vide. Utilisé par les lots 02 et 03.

### Exercice
* exerciseType : 'technique', 'force' ou 'muscu'. Défaut calculé : Lifting avec liftBaseMode 'oly' donne 'technique', Lifting avec liftBaseMode 'force' donne 'force', toute autre catégorie donne 'muscu'. Lot 10.
* progressionStep : pas de montée en kg pour la double progression. Défaut : valeur des réglages (2,5). Lot 04.
* autoProgression : booléen, défaut true. Lot 04.
* deloadMuscu : booléen, défaut true, utile pour les exercices de muscu. Lot 13 (reporté depuis le lot 09 : LOT-09.md le listait aussi, mais aucune fonction ne le lit avant R8/lot 13 ; un interrupteur sans effet n'a pas été construit).

### Série de séance
* result : 'ok', 'fail' ou null (haltérophilie). Lot 05.
* repResults : tableau de booléens, un par rep (true = réussie). Lot 05.
* repsDone : nombre de reps réussies pour le mode compteur. Lot 05.
* failRep : numéro de la rep ratée (1 à N) ou null. Lot 05.
* failCause : 'devant', 'derriere', 'reception', 'pas_tire', 'autre' ou null. Lot 05.
* note : texte libre. Lot 05.
* targetReps : nombre de reps visé par la double progression. Lot 04.

### Exercice de séance
* block : 'cycle' (mouvement piloté par un cycle) ou 'muscu'. Calculé à la construction de la séance. Lot 11.
* deload : booléen, true si la séance est allégée. Lot 13.

### Cycle de force
Garder les champs existants et ajouter :
* historique_cycles : tableau de { cycle, debut, fin, seances, seances_prevues, reussite_pct, one_rm_avant, one_rm_apres }. Lot 06.
* prochain_cycle : identifiant du cycle tiré en attente de validation, ou null. Lot 06.
* en_attente_de_validation : booléen. Lot 06.
* decalage_semaines : nombre de semaines avant le démarrage, résultat de la coordination. Lot 08. Il se traduit en forceCycleStartDate pour réutiliser le mécanisme existant.

### Réglages
Ajouter, avec les valeurs par défaut suivantes :
* defaultProgressionStep : 2.5
* defaultRepRange : { min: 8, max: 10 }
* restByType : { technique: 150, force: 120, muscu: 90 } en secondes
* barWeightKg : 20
* deloadMuscu : true
* heavyThreshold : 85 (pourcentage à partir duquel une semaine est lourde)
* maxHeavyCyclesPerWeek : 2
* j2OffsetPoints : 10 (baisse de la deuxième séance de la semaine, R12)
* lastImportAt : null

## Migration d'un cycle déjà en cours

Les cycles 'A' à 'E' continuent de fonctionner : ils restent définis dans FORCE_CYCLES sous ces clés. Ne jamais renommer ou supprimer ces clés. Seul l'affichage change : Cycle 13 à Cycle 17 (A = 13, B = 14, C = 15, D = 16, E = 17). Ils font partie du tirage, qui porte sur 17 cycles.

## Test de migration

1. Importer un export fait avant le lot.
2. Vérifier que les routines, séances, exercices et cycles sont identiques.
3. Vérifier que les nouveaux champs ont leur valeur par défaut.
4. Exporter, réimporter, comparer : le résultat doit être identique.
