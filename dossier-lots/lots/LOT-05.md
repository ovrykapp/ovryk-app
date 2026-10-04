# LOT 05. Séance d'haltérophilie : réussi ou raté

Taille : L. Dépend de : 04.

## Écrans de la maquette

* ../maquette/03-seance-halterophilie.png
* ../maquette/10-haltero-un-rate.png
* ../maquette/11-haltero-serie-longue.png

## Objectif

Créer le mode de séance des mouvements pilotés par un cycle : charge en pourcentage du 1RM, réussite par rep, saisie d'un raté, compteur pour les séries longues.

## Existant à connaître

* Pour un mouvement avec cycle, buildSessionFromRoutine construit les séries depuis getCycleWeek (percent1rm, reps) et fige le 1RM (oneRepMaxSnapshot).
* buildLiveSessionSetRow affiche la charge calculée (computeWeightFromPercent) sans saisie de réussite : une série est simplement faite ou non.

## À faire

1. Détecter le mode : un exercice de séance est en mode haltérophilie si sex.category est Lifting et si un cycle actif ou un mode de base le pilote.
2. Écran principal (maquette 3) : carte de charge avec la charge en grand, boutons moins 2,5 et plus 2,5, rappel "72 % de ton 1RM de 90 kg", pastilles de pourcentage proches, et chargement par côté.
3. "Réussite par série" : une ligne par série avec les ronds Rep 1, Rep 2 (jusqu'à 3 reps). Rond bleu = réussie, rond orange avec croix = ratée, rond en pointillés = à valider.
4. Boutons du bas : note, "Un raté", "Série réussie". "Série réussie" valide toutes les reps et passe à la série suivante en lançant le repos.
5. "Un raté" (maquette 10) : feuille en bas avec "Quelle rep ?" (boutons Rep 1 à N), "Pourquoi ?" (devant, derrière, en réception, pas tiré, autre), rappel du taux de réussite à cette charge, boutons "Enregistrer le raté" et "Annuler". Écrit result, repResults, failRep, failCause.
6. Mode compteur (maquette 11) pour les séries de 4 reps ou plus : grand compteur "5 sur 5" avec moins et plus, qui part de l'objectif. Écrit repsDone.
7. Semaines de test : afficher la liste des tentatives (voir lot 06) au lieu du tableau habituel.
8. Taux de réussite : fonction qui, pour un exercice et une charge, calcule reps réussies sur reps tentées dans l'historique. Utilisée dans la feuille du raté et dans le détail d'une séance (lot 12).
9. Une série ratée reste enregistrée comme faite (done) avec result 'fail', pour que le volume et l'historique restent cohérents ; le volume ne compte que les reps réussies.

## Données

set.result, set.repResults, set.repsDone, set.failRep, set.failCause, set.note.

## Règles métier concernées

R6 (haltérophilie), R2 (charge), R10 (repos).

## Critères d'acceptation

* "Série réussie" valide toutes les reps en un appui et lance le repos.
* "Un raté" enregistre la rep et la cause, et la série reste ratée dans l'historique.
* Une série de 5 reps utilise le compteur.
* Le taux de réussite affiché est juste sur un jeu de données de test.
* Le volume d'une séance ne compte pas les reps ratées.
* Une séance interrompue puis reprise conserve les réussites et les ratés.
* Les anciennes séances (sans result) s'affichent sans erreur.

## Risques

* Le plus gros lot : le découper en trois livraisons (écran principal, raté, compteur) si besoin.
* computeSetVolume doit gérer les séries ratées sans changer le volume des anciennes séances.

## Hors lot

La saisie des tentatives d'un test (lot 06) et le séparateur de bloc (lot 11).

## Prompt pour Claude Code

Copie ce texte dans Claude Code, à la racine du projet, après avoir exporté tes données et fait un commit :

> Lis CLAUDE.md et les documents du dossier dossier-lots : METHODE.md, ETAT-DES-LIEUX.md, MODELE-DE-DONNEES.md, REGLES-METIER.md, puis lots/LOT-05.md et les images de maquette citées. Travaille uniquement sur le lot 05. Commence par me proposer un plan des modifications, sans écrire de code, en citant les fonctions et les identifiants que tu comptes toucher. Attends ma validation. Ensuite modifie index.html par petites étapes, vérifie la syntaxe du script, lance node outils/verifier-cycles.js, teste dans un navigateur à 390 x 844 et passe les critères d'acceptation un par un. Ne touche à rien d'autre. Si une règle est ambiguë, pose moi la question.
