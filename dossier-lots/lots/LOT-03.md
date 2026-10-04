# LOT 03. Accueil : séance du jour

Taille : M. Dépend de : 02.

## Écrans de la maquette

* ../maquette/01-accueil.png

## Objectif

Reconstruire l'accueil comme dans la maquette : date et titre "Séance du jour", semaine en pastilles, carte de la séance, deux statistiques, bandeau du prochain test 1RM.

## Existant à connaître

* Fonctions : renderDashboardHero, renderDashboardWeekSummary, renderDashboardLastSession, renderDashboardProgress, renderDashboardForceCycles, renderDashboardStagnation, renderCycleAlertBanner, renderDashboardHome (appelle les précédentes).
* computeNextRoutine choisit la routine la moins récemment terminée. estimateRoutineDuration estime la durée. sessionVolume calcule le volume d'une séance.
* Les identifiants #dash-hero, #dash-force-cycles, #dash-stagnation, #dash-week-summary, #dash-last-session, #dash-progress.

## À faire

1. En-tête de l'accueil : date du jour en français ("Samedi 3 octobre") et titre "Séance du jour" en Barlow Condensed, bouton engrenage à droite (lot 01).
2. Bande de la semaine : sept pastilles L M M J V S D avec le numéro du jour. Le jour courant est plein orange. Un point bleu sous un jour où une séance a été terminée. Un jour sans séance prévue est grisé.
3. Carte de la séance : choisir la routine du jour avec cette règle : une routine dont weekdays contient aujourd'hui, sinon computeNextRoutine. Afficher les pastilles HALTÉRO et MUSCU, le nom de la routine, "N exercices, environ X h Y" et la semaine du cycle principal ("Semaine 3 sur 8"). Puis la liste des exercices avec leur prescription : pour un mouvement de cycle, "séries x reps à pourcentage" de la semaine en bleu ; pour la muscu, "séries x plage". Bouton "Commencer la séance".
4. Deux tuiles : "Séances cette semaine" (réalisées sur prévues, prévues = nombre de jours avec routine, à défaut 4) et "Volume cette semaine" (somme de sessionVolume des séances de la semaine, en kg).
5. Bandeau du prochain test 1RM : le mouvement dont le test est le plus proche, avec "dans N semaines". Si un test est dû cette semaine, afficher l'alerte actuelle de renderCycleAlertBanner à la place.
6. Retirer de l'accueil : la liste des cycles en cours (déplacée au lot 02), le hero "Crée ta première routine" sauf s'il n'existe aucune routine (état vide à conserver), la dernière séance et la progression récente. Garder la stagnation seulement si elle apparaît, sous les tuiles.
7. Si aucune routine n'existe, garder un état vide avec un bouton de création.

## Données

Aucun nouveau champ. Utilise routine.weekdays (lot 02).

## Règles métier concernées

R7 pour trouver le prochain test, R2 pour les pourcentages affichés.

## Critères d'acceptation

* La bande de la semaine reflète les séances réellement terminées.
* La carte affiche la routine du jour d'aujourd'hui, ou la routine suivante en rotation si aucun jour n'est défini.
* "Commencer la séance" démarre cette routine dans l'onglet Séance.
* Les deux tuiles donnent les bons chiffres sur un jeu de données de test.
* Le bandeau affiche le bon prochain test.
* Sans routine, l'accueil affiche un état vide propre.

## Risques

* Le calcul des semaines doit commencer le lundi (startOfWeek existe).
* Ne pas supprimer les fonctions renderDashboard* encore utilisées ailleurs : les vider ou les appeler moins, mais vérifier les références.

## Hors lot

Le bandeau "À surveiller" et la décharge (lot 13).

## Prompt pour Claude Code

Copie ce texte dans Claude Code, à la racine du projet, après avoir exporté tes données et fait un commit :

> Lis CLAUDE.md et les documents du dossier dossier-lots : METHODE.md, ETAT-DES-LIEUX.md, MODELE-DE-DONNEES.md, REGLES-METIER.md, puis lots/LOT-03.md et les images de maquette citées. Travaille uniquement sur le lot 03. Commence par me proposer un plan des modifications, sans écrire de code, en citant les fonctions et les identifiants que tu comptes toucher. Attends ma validation. Ensuite modifie index.html par petites étapes, vérifie la syntaxe du script, lance node outils/verifier-cycles.js, teste dans un navigateur à 390 x 844 et passe les critères d'acceptation un par un. Ne touche à rien d'autre. Si une règle est ambiguë, pose moi la question.
