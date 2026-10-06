# Carte des écrans

Pour chaque écran de la maquette : l'image, le lot, la cible dans Ovryk et ce qu'il faut faire.
Légende : Refaire = écran existant à reconstruire. Créer = n'existe pas. Adapter = lire ECRANS-A-ADAPTER.md.

| N° | Écran | Image | Lot | Cible dans Ovryk | Action |
|---|---|---|---|---|---|
| 1 | Accueil | maquette/01-accueil.png | 03 | view-dashboard (bande de la semaine cliquable depuis, hors lot : renderDashboardWeekStripWired, panneau du jour renderDashboardDayPanel, bouton "Autre séance" vers Programme) | Refaire |
| 2 | Séance muscu | maquette/02-seance-muscu.png | 04 | séance active : buildLiveSessionExercise, buildLiveSessionSetRow | Refaire |
| 3 | Séance haltérophilie | maquette/03-seance-halterophilie.png | 05 | séance active, mode haltérophilie | Créer |
| 4 | Programme | maquette/04-programme.png | 02 | view-routine (liste de la semaine retirée depuis, hors lot ; "Mes séances" dans renderRoutineList sans pastilles de jours ; bande de 7 jours réutilisée de l'Accueil via renderDashboardWeekStrip, avec panneau du jour renderProgrammeDayPanel) | Refaire |
| 5 | Progrès | maquette/05-progres.png | 12 | view-progression (déjà riche) : style seulement, bouton Historique | Restyler |
| 6 | Fiche exercice | maquette/06-fiche-exercice.png | 10 | openExerciseDetail | Refaire |
| 7 | Nouveau programme | maquette/07-nouveau-programme.png | 09 | création de routine | Refaire |
| 8 | Vérifier l'import | maquette/08-verifier-l-import.png | 15 | écran de vérification de l'import CSV | Adapter |
| 9 | Charges de départ | maquette/09-charges-de-depart.png | 09 | étape facultative des 1RM et charges de départ | Créer |
| 10 | Haltéro, un raté | maquette/10-haltero-un-rate.png | 05 | feuille "Un raté" | Créer |
| 11 | Haltéro, série longue | maquette/11-haltero-serie-longue.png | 05 | compteur de reps | Créer |
| 12 | Type d'exercice | maquette/12-type-d-exercice.png | 10 | type d'exercice | Créer |
| 13 | Séparateur de bloc | maquette/13-separateur-de-bloc.png | 11 | séparateur de bloc | Créer |
| 14 | Historique | maquette/14-historique.png | 12 | liste globale des séances | Créer |
| 15 | Détail d'une séance | maquette/15-detail-d-une-seance.png | 12 | détail d'une séance | Créer |
| 16 | Réglages | maquette/16-reglages.png | 14 | view-profil | Refaire |
| 17 | Barre et disques | maquette/17-barre-et-disques.png | 14 | barre et disques (constante BAR_WEIGHT_KG, settings.plateSet) | Refaire |
| 18 | Compte et sauvegarde | maquette/18-compte-et-sauvegarde.png | 16 | compte et synchronisation | Créer |
| 19 | Importer mes données | maquette/19-importer-mes-donnees.png | 15 | import de données | Créer |
| 20 | Créer un programme | maquette/20-creer-un-programme.png | 09 | routine-editor-view | Adapter |
| 21 | Éditer une séance | maquette/21-editer-une-seance.png | 09 | routine-editor-view : liste des exercices | Adapter |
| 22 | Configurer l'exercice | maquette/22-configurer-l-exercice.png | 07 | réglage d'une semaine de cycle | Adapter |
| 23 | Configurer un exercice muscu | maquette/23-configurer-un-exercice-muscu.png | 09 | réglage d'un exercice de muscu dans l'éditeur | Créer |
| 24 | Tirer mes cycles | maquette/24-tirer-mes-cycles.png | 07 | activation de plusieurs cycles | Adapter |
| 25 | Détail d'un cycle | maquette/25-detail-d-un-cycle.png | 07 | cycle-detail-page | Adapter |
| 26 | Test 1RM séparé | maquette/26-test-1rm-separe.png | 06 | test 1RM : tentatives | Refaire |
| 27 | Fin de cycle | maquette/27-fin-de-cycle.png | 06 | fin de cycle et prochain cycle | Adapter |
| 28 | Charge de la semaine | maquette/28-charge-de-la-semaine.png | 13 | charge de la semaine | Créer |
| 29 | Cycles tirés au sort | maquette/29-cycles-tires-au-sort.png | 07 | résultat du tirage | Adapter |
| 30 | Coordination des cycles | maquette/30-coordination-des-cycles.png | 08 | coordination des cycles | Adapter |

## Notes

* L'écran 5 (Progrès) n'a pas de lot propre : la vue Progrès d'Ovryk est plus complète que la maquette (groupes musculaires, graphiques, détail par exercice). Seuls le style (lot 00) et le bouton Historique (lot 12) changent.
* Les écrans 20 et 21 ne sont pas des écrans neufs : c'est l'éditeur de routine existant, à restyler.
* Les écrans marqués Adapter montrent encore des cycles propres à un mouvement : voir ECRANS-A-ADAPTER.md.
