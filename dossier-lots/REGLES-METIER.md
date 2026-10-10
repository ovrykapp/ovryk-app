# Règles métier

Chaque règle porte un numéro, que les lots citent. Les valeurs entre parenthèses sont des réglages à pouvoir modifier.

## R1. Cycles génériques

* Il existe 12 cycles génériques, identifiants '1' à '12', applicables à n'importe quel mouvement. Ils sont définis dans FORCE_CYCLES et documentés dans docs/CYCLES.md du zip ovryk-maquette.
* Les cycles 'A' à 'E' deviennent les cycles 13 à 17 à l'affichage (A = Cycle 13, B = Cycle 14, C = Cycle 15, D = Cycle 16, E = Cycle 17). Leurs identifiants internes 'A' à 'E' ne changent pas, pour ne pas casser les cycles déjà en cours. Ils durent 6 semaines avec le test 1RM inclus en semaine 6, comme le cycle 12. Ils entrent dans le tirage : il y a donc 17 cycles au total.
* Durée : 8 semaines avec le test 1RM en semaine 8 (cycles 1, 2, 6, 7), 7 semaines avec un test 1RM séparé en semaine 7 (cycles 3, 4, 5, 8, 9, 10, 11), 6 semaines avec un test inclus en semaine 6 (cycle 12).
* Une semaine de cycle est une liste de séries { reps, percent }. Les semaines allégées portent un drapeau deload (à ajouter au lot 13).

## R2. Charge

* charge = arrondi au multiple de 2,5 kg le plus proche de 1RM x pourcentage. C'est le comportement de computeWeightFromPercent.
* Le 1RM de référence d'une séance est figé dans la séance (oneRepMaxSnapshot). Changer le 1RM ne réécrit jamais les séances passées.

## R3. Test de 1RM

* Un test est une suite de tentatives de charge croissante, chacune réussie ou ratée.
* Le nouveau 1RM proposé est la charge de la meilleure tentative réussie. L'utilisateur peut le corriger ou garder son 1RM actuel.
* Après validation, le cycle se termine : l'écran de fin de cycle propose le prochain cycle. Il ne démarre qu'après confirmation.

## R4. Tirage du prochain cycle

* Tirer au hasard parmi les 17 cycles (les 12 génériques et les cycles A à E affichés 13 à 17), en excluant le cycle qui vient de se terminer sur ce mouvement.
* Préférer un cycle qui n'est pas déjà actif sur un autre mouvement. Si tous le sont, autoriser (DECISIONS-A-PRENDRE n° 11).
* Le tirage s'applique au cycle, jamais au mouvement : c'est l'utilisateur qui choisit les mouvements.
* Le résultat peut être relancé (une ou toutes les lignes), gardé identique, ou remplacé par un choix manuel.

## R5. Double progression (muscu)

* Chaque exercice a une plage de reps (par défaut 8 à 10) et un pas de montée (par défaut 2,5 kg).
* Si toutes les séries n'ont pas atteint le haut de la plage : même charge, objectif de reps = reps de la série la plus faible + 1, sans dépasser le haut de la plage.
* Si toutes les séries ont atteint le haut de la plage : la charge monte du pas, les reps repartent au bas de la plage.
* Si une série tombe sous le bas de la plage : même charge, pas de baisse. Après deux séances de suite dans ce cas, proposer une baisse de 5 à 10 % sans l'imposer.
* La suggestion est toujours modifiable. Option de désactivation par exercice (autoProgression).

> 2026-10-09 : règle retirée — "Si le RPE saisi est 10 alors que la plage est atteinte : afficher un avertissement avant la montée, sans la bloquer." La saisie du RPE a été retirée de l'interface de séance (point D.2) ; set.rpe, son calcul (resolveDoneSets, getExerciseSessionRecords) et l'export restent intacts, seul l'avertissement disparaît avec l'interface qui le déclenchait.

## R6. Haltérophilie : réussi ou raté

* Une série est validée en un appui ("Série réussie") : toutes les reps sont réussies.
* "Un raté" ouvre une saisie : quelle rep, quelle cause. Les autres reps de la série restent réussies par défaut.
* Séries de 4 reps ou plus : compteur de reps réussies, sans détail par rep.
* Taux de réussite d'une charge = reps réussies divisé par reps tentées, sur l'historique de cet exercice.
* Causes proposées : devant, derrière, en réception, pas tiré, autre.
* Après un raté, la série s'arrête : les reps suivantes ne sont pas tentées et ne comptent ni dans le volume ni dans le taux de réussite. Limite connue : on ne gère pas plusieurs ratés dans une même série.

## R7. Coordination des cycles

* Une semaine de cycle est lourde si c'est une semaine de test, ou si le pourcentage maximal de la semaine est supérieur ou égal à 85 (heavyThreshold).
* Règle : pas plus de 2 cycles lourds la même semaine (maxHeavyCyclesPerWeek).
* À l'activation et à chaque renouvellement, calculer le plus petit décalage de départ, en semaines, qui respecte la règle pour tous les cycles actifs. Chercher jusqu'à 8 semaines. Sans solution, garder le décalage 0 et afficher un avertissement.
* Pendant l'attente, le mouvement reste en mode de base (technique ou charge fixe), déjà géré par isBeforeForceCycleStart.
* Le décalage est modifiable à la main, semaine par semaine.

## R8. Décharge de la muscu

* Une séance est allégée quand au moins un cycle actif est dans une semaine allégée (drapeau deload) et que le réglage deloadMuscuMode vaut 'auto', ou quand l'utilisateur appuie sur "Alléger cette séance" en mode 'manual'. En mode 'off' (valeur par défaut, champ absent), rien n'est allégé (décision du 2026-10-10, lot 13).
* Les exercices de muscu perdent un tiers de leurs séries, arrondi à l'entier le plus proche, avec un minimum de 2 séries. La charge ne change pas.
* L'allègement est affiché dans la séance et peut être ignoré en un geste.

## R9. Charge de la semaine

* Séries par jour : nombre de séries validées ou prévues par jour de la semaine, haltérophilie et muscu séparées.
* Séries par groupe musculaire : réutiliser computeWeeklySeriesCounts et PROGRESSION_GROUPS. Un groupe est signalé "élevé" au dessus de 1,3 fois son objectif hebdomadaire.
* Chevauchement musculaire : si une même zone (par exemple le bas du dos) est sollicitée par au moins 3 séries dans deux séances espacées de moins de 48 heures, afficher un avertissement léger avec "Déplacer une séance" et "Je garde".
* Les zones sollicitées par exercice sont déclarées dans une table (lot 13), à commencer par : bas du dos (soulevés de terre, rowing barre, extensions lombaires, tirages et épaulés lourds), jambes, épaules.

## R10. Repos

* Durée de repos par défaut par type d'exercice : technique 150 s, force 120 s, muscu 90 s (restByType).
* Une semaine de cycle peut imposer sa propre durée (restSeconds) : elle prime.

## R11. Pas de compte obligatoire

* L'application fonctionne sans compte, avec les données dans le navigateur.
* Le compte est proposé après quelques séances et sert à la sauvegarde. Connexion par Google ou lien envoyé par e-mail.

## R12. Deux séances par semaine pour un mouvement

* Un mouvement piloté par un cycle peut figurer dans deux routines de la même semaine (deux jours différents).
* La première séance de la semaine suit le cycle tel quel. La deuxième est plus légère : tous les pourcentages baissent de 10 points (réglage j2OffsetPoints), sans descendre sous 50 %, avec les mêmes reps.
* Le cycle ne change pas de semaine à la deuxième séance : la semaine du cycle avance une seule fois par semaine civile.
* Le test de 1RM n'est jamais une deuxième séance : il reste la première.
