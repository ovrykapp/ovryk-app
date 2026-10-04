# LOT 08. Coordination des cycles

Taille : M. Dépend de : 07.

## Écrans de la maquette

* ../maquette/30-coordination-des-cycles.png

## Objectif

Décaler le départ des cycles pour ne jamais avoir plus de 2 cycles lourds la même semaine, avec un calendrier lisible et des départs modifiables.

## Existant à connaître

* Le décalage existe par exercice : forceCycleStartDate, isBeforeForceCycleStart, getWeeksUntilForceCycleStart, maybeAutoActivateForceCycle, refreshScheduledForceCycleActivations. Avant la date, le mouvement est en mode de base.
* Aucune règle ne choisit ces dates.

## À faire

1. Fonction isHeavyWeek(semaine) : vrai si isTestWeek ou si le pourcentage maximal de la semaine est supérieur ou égal à heavyThreshold (R7).
2. Fonction computeHeavyCounts(cycles avec décalages) qui renvoie, pour chaque semaine du programme, le nombre de cycles lourds.
3. Fonction suggestStartOffsets(cycles) : pour chaque cycle, dans l'ordre, trouver le plus petit décalage (0 à 8 semaines) qui garde tous les comptes à maxHeavyCyclesPerWeek au plus. Sans solution, décalage 0 et avertissement.
4. Utiliser cette fonction à la validation du lot 07 et au lancement du lot 06 : le décalage devient forceCycleStartDate (date du lundi concerné) et decalage_semaines.
5. Écran "Coordination" (maquette 30) : tableau de 12 semaines, une ligne par mouvement actif, cases Volume (bleu sombre), Allégée (pointillés bleus, lettre A), Pic (orange, P) ou Test (orange, T). Ligne "En pic ou test" avec le nombre par semaine, en orange à 2.
6. Liste "Départ de chaque cycle" avec moins et plus pour décaler d'une semaine ; le tableau se recalcule immédiatement. Avertissement si la règle est dépassée.
7. Accès depuis la carte Cycles en cours de l'écran Programme et depuis l'écran de résultat du tirage (lot 07).

## Données

cycle.decalage_semaines, settings.heavyThreshold, settings.maxHeavyCyclesPerWeek.

## Règles métier concernées

R7 (coordination).

## Critères d'acceptation

* Avec quatre cycles activés ensemble, aucun pas plus de 2 cycles lourds la même semaine.
* Un décalage manuel est respecté et le tableau le montre.
* Un mouvement décalé reste en mode de base avant son départ.
* Une règle impossible à respecter affiche un avertissement et ne bloque rien.
* Le calcul est identique après fermeture et réouverture de l'application.

## Risques

* Mélange de dates et de numéros de semaine : choisir le lundi comme référence partout.
* Un cycle A à E déjà en cours compte comme un cycle avec ses propres semaines lourdes.

## Hors lot

L'alerte de chevauchement musculaire (lot 13).

## Prompt pour Claude Code

Copie ce texte dans Claude Code, à la racine du projet, après avoir exporté tes données et fait un commit :

> Lis CLAUDE.md et les documents du dossier dossier-lots : METHODE.md, ETAT-DES-LIEUX.md, MODELE-DE-DONNEES.md, REGLES-METIER.md, puis lots/LOT-08.md et les images de maquette citées. Travaille uniquement sur le lot 08. Commence par me proposer un plan des modifications, sans écrire de code, en citant les fonctions et les identifiants que tu comptes toucher. Attends ma validation. Ensuite modifie index.html par petites étapes, vérifie la syntaxe du script, lance node outils/verifier-cycles.js, teste dans un navigateur à 390 x 844 et passe les critères d'acceptation un par un. Ne touche à rien d'autre. Si une règle est ambiguë, pose moi la question.
