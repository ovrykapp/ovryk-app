# CLAUDE.md : Ovryk

Guide de contexte pour Claude Code. Ovryk est une app de suivi de musculation et d'haltérophilie, usage strictement personnel (Ruben, solo, pas de multi utilisateur, pas d'authentification).

## Mission en cours

Remplacer entièrement l'interface actuelle par celle de la maquette (dossier `maquette/`, 30 images) et ajouter les nouvelles fonctions décrites dans `docs/ovryk_modifications.md`.

* L'ancienne interface peut être supprimée et remplacée : tout le CSS, le HTML des vues et les rendus d'écran peuvent être réécrits. Ruben a une sauvegarde de l'app d'origine (`index.v1.html`) et de ses données (`backups/`).
* La couche de données (`OvrykDB`, clés `ovryk.*`, import et export) reste. L'export du 1er octobre 2026 (`backups/ovryk-export-2026-10-01.json`) doit continuer de s'importer. Si Ruben décide un jour de repartir de zéro côté données, il supprimera cette ligne lui même.
* En cas de contradiction entre le document, le code et l'export : **le code et l'export ont raison**.

## Règles de travail

* Réponds en français.
* Un lot à la fois, dans l'ordre de la section "Plan de travail". Ne commence jamais un lot suivant sans l'accord de Ruben.
* Avant de coder : propose un plan avec les fichiers, les fonctions et les risques, puis attends l'accord.
* Les chiffres de la maquette sont des exemples. Les cycles viennent de `data/cycles_generiques.json`.
* Ne modifie jamais `backups/`, `docs/` ni `index.v1.html` (lecture seule).
* Un commit par lot validé, avec un message descriptif. Ne fais jamais de `git push` sans l'accord explicite de Ruben.
* À la fin de chaque lot : donne la liste de ce que Ruben doit tester à la main, puis propose le commit.
* Prompts pour Claude Code : texte brut, structuré, prêt à coller directement dans VS Code.

## Stack et principes

* Fichier unique `index.html` : HTML, CSS et JavaScript vanilla, aucun framework, aucun build step. **Ne pas découper en plusieurs fichiers.**
* Persistance via `localStorage` uniquement, aucun backend.
* **Ne jamais proposer Next.js, React, Supabase, Firebase ou un backend** : refusé explicitement, l'app reste un fichier statique déployable tel quel. La sauvegarde reste l'export JSON, avec le rappel existant (`renderBackupReminder`).
* PWA installable (`manifest.json`, `sw.js`, meta apple-mobile-web-app, zoom lock en mode standalone).
* Tout le JS est dans une IIFE unique `(function () { ... })();` en fin de fichier. `OvrykDB` est exposé globalement (`window.OvrykDB`).
* ES5 volontairement (`var`, `function`, pas d'arrow functions, pas de classes) : rester dans ce style, ne pas introduire d'ES6+ sans discussion.
* Interface entièrement en français (labels, noms de variables métier comme `cycle_actif`, `semaine_actuelle`, `one_rm_actuel`), commentaires en anglais.
* Aucune dépendance externe, sauf les polices Google Fonts. Ajouter les fichiers de police au cache de `sw.js` pour le mode hors ligne.
* Pas de `window.confirm()` natif : utiliser le confirm modal existant.
* Toute nouvelle clé de données passe par `DB_KEYS` et une fonction dédiée sur `OvrykDB` (get et save), jamais d'accès direct à `localStorage` ailleurs.
* Toute modification du catalogue d'exercices par défaut passe par le mécanisme de migration (`EXERCISE_RENAMES` pour un renommage, ajout dans `DEFAULT_EXERCISE_DEFS` ou `LIFTING_DEFS` pour un nouveau mouvement).
* Les mouvements Lifting sont programmés en % du 1RM stocké, jamais en poids absolu au niveau de la routine.
* Toute migration de données est idempotente, garde une copie `ovryk.backup.<date>` et ne supprime jamais de séance. Il existe une séance `in_progress` jamais terminée (UPPER B du 28/09) : la conserver, ne pas la nettoyer automatiquement.

## Écarts avec docs/ovryk_modifications.md (ce fichier prime)

* Lot 0 du document (découpage en `index.html`, `styles.css`, `app.js`) : annulé. Le fichier reste unique.
* Lot 13 du document (compte et sauvegarde en ligne, Supabase ou Firebase) : annulé. Les écrans Compte et sauvegarde de la maquette ne sont pas à construire.
* Lots 7 et 8 : la double progression, les objectifs hebdomadaires par groupe musculaire et les notifications existent déjà. Adapter l'existant, ne pas le recréer.
* Schéma de données : le document reprend un ancien commentaire du code. Le schéma réel est celui de la section suivante.
* Écran "Importer mon programme" de la maquette (lecture d'une photo ou d'un PDF) : hors périmètre.

## Schéma de données (constaté dans l'export réel du 1er octobre 2026)

Clés (`DB_KEYS`) : `ovryk.exercises`, `ovryk.routines`, `ovryk.sessions`, `ovryk.settings`, `ovryk.forceCycles`. Le commentaire de schéma dans l'ancien code est périmé : en cas de doute, lire `OvrykDB` et l'export.

```
Exercise    { id, name, category, equipment, unit, isCustom, oneRepMax?,
              forceCycleStartDate?, lastGrip?, createdAt }
Routine     { id, name, createdAt, updatedAt,
              exercises: [ { id, exerciseId, restSeconds, groupId?, groupType?,
                sets: [ { id, repType:'range', repsMin, repsMax, weightKg }
                      | { id, repType:'fixed', reps, percent1rm } ] } ] }
Session     { id, routineId, routineName, date, startedAt, completedAt,
              status:'in_progress'|'completed', durationSeconds, notes,
              exercises: [ { id, exerciseId, exerciseName, category,
                oneRepMaxSnapshot, restSeconds, groupId, groupType,
                sets: [ { id, repType, repsMin, repsMax, weightKg,
                          reps, percent1rm, done, rpe, repsActual } ] } ] }
Settings    { unit, restTimerSeconds, lastExportAt,
              muscleGroupTargets: { pecs, dos, epaules, bras, quadriceps,
                                    ischios, fessiers, mollets, abdominaux },
              notificationPrefs: { seance, repos, resume }, plateSet? }
ForceCycle  { exercise_id, cycle_actif, one_rm_actuel, semaine_actuelle,
              historique_1rm: [ { date, valeur } ] }
              Une seule clé par exercise_id, uniquement pour category 'Lifting'.
```

`CATEGORIES` : Pecs, Dos, Épaules, Bras, Jambes, Abdos, Lifting. `EQUIPMENT_LIST` : Barre, Haltères, Poulie, Machine, Poids du corps, Autre.

## Ce qui existe déjà (à garder ou restyler, jamais réécrire sans raison)

* Double progression hors Lifting : `applyRangeProgression` (série faite au haut de la plage, charge plus 2,5 kg la fois suivante), préremplissage depuis la dernière séance, indication de la dernière performance (`formatLastSessionHint`).
* Détection de stagnation (`detectStagnation`), objectifs hebdomadaires par groupe musculaire (`muscleGroupTargets`, vue Progression), notifications (`notificationPrefs`).
* Timer de repos, RPE par série, supersets (`groupId`, `groupType`), rappel de la semaine de test sur le Dashboard.
* Calculateur de plaques (`computePlateLoad`, `buildPlateStackVisual`, jeu de disques éditable, défaut `[25, 20, 15, 10, 5, 2.5, 1.25]` kg).
* Migration douce du catalogue (`migrateExerciseCatalog`), export et import de toutes les données.

## Cycles de force

Existant : 5 cycles de 6 semaines (A à E, `FORCE_CYCLES`), `tirerProchainCycle` (tire parmi les cycles hors celui qui vient de finir), un cycle actif par mouvement Lifting (`activateForceCycle`, `advanceForceCycleWeek`, `submitNewOneRM`, `deactivateForceCycle`, `maybeAutoActivateForceCycle`), départ décalé via `forceCycleStartDate`. La durée de 6 semaines est écrite en dur à plusieurs endroits (avancement de semaine, affichages "/6", formulaire de test à la semaine 6) : à généraliser.

Cible : 12 cycles génériques (`data/cycles_generiques.json`), valables pour n'importe quel mouvement, de 6 ou 8 semaines. Le tirage choisit le cycle, pas le mouvement.

* Test 1RM : cycles de 8 semaines, en semaine 8. Cycles de 6 semaines, séance de test séparée après la semaine 6, y compris les cycles 4 et 12.
* Les semaines allégées baissent l'intensité, pas forcément le volume : utiliser `lightWeek` et `isLightWeek`, jamais un calcul sur le volume.
* Coordination : jamais plus de 2 mouvements en pic ou en test la même semaine, départs décalés (`forceCycleStartDate`), semaines allégées alignées quand c'est possible.
* Fin de cycle : nouveau 1RM (pré rempli avec la meilleure charge réussie), cycle suivant tiré parmi les 11 autres, recalcul pour le futur seulement. Les séances passées gardent les charges réellement soulevées.
* Les cycles A à E restent valables pour les cycles déjà actifs (export du 1er octobre : Deadlift en cycle C semaine 2, Back Squat en cycle D semaine 1). Ruben choisit au lot 2 de les reprendre ou de les relancer avec un cycle tiré parmi les 12. Ne plus tirer A à E ensuite.

## Design à appliquer (remplace l'identité visuelle actuelle)

Dark, très contrasté. Orange = muscu et action principale. Bleu glacé = haltérophilie. Détails complets dans la section 6 du document.

* Couleurs : fond `#111110`, surface `#1B1B19`, surface élevée `#252522`, bordure `#2E2E2A`, barre du bas `#161614`, texte `#F2EFE8`, texte secondaire `#A8A59B`, accent `#FF6A2B`, texte accent `#FF8A55`, fond muscu `#3A2216`, haltérophilie `#8EBBFF`, fond haltérophilie `#1E2A3D`.
* Polices : Barlow Condensed 700 en majuscules pour les titres et les grosses charges, Barlow pour le texte. Remplacent Inter Tight.
* Composants : bouton principal 56 px de haut, rayon 14 px ; chips 44 px, rayon 22 px ; cartes rayon 16 px avec bordure 1 px ; zones tactiles de 44 px minimum ; barre du bas de 84 px avec bouton central orange.
* Navigation cible : Accueil, Programme, bouton central (démarrer une séance), Progrès, Exercices. Les Réglages passent derrière une icône en haut de l'Accueil.
* Garder les hover sous `@media (hover: hover) and (pointer: fine)`. Les couleurs de bordure restent des `color-mix()` calculés à partir de `--ink` : ne pas les figer en dur.

## Plan de travail (un lot par conversation)

Avant le lot 0 : audit en lecture seule. Comparer le document, le code et l'export, et lister ce qui existe déjà, les différences de format de données et les risques pour les 2 cycles actifs et la séance non terminée.

0. Préparation : vérifier que `index.v1.html` est identique à `index.html` et que git est propre. Aucun découpage de fichier.
1. Design : remplacement complet de l'interface, variables, polices, navigation, composants, coquille des écrans.
2. Cycles : 12 cycles génériques, durée de 6 ou 8 semaines, cycles historiques A à E.
3. Tirage et départs décalés.
4. Coordination et calendrier.
5. Test 1RM séparé et fin de cycle.
6. Séance haltérophilie : série réussie, raté avec rep et cause, compteur à partir de 4 reps, séparateur de bloc.
7. Muscu libre : adapter la double progression existante (palier réglable, baisse après deux séances ratées, avertissement RPE, objectif du jour, type d'exercice).
8. Volume et alertes : réutiliser les 9 groupes de `muscleGroupTargets`, ajouter le volume par jour et l'alerte à moins de 48 heures.
9. Historique et progrès.
10. Réglages et matériel : barre et disques à partir du calculateur de plaques existant.
11. Accueil et programme.
12. Finitions : accessibilité, contraste, vérification des anciens exports.

## Tests manuels après chaque lot

* L'app s'ouvre sans erreur dans la console du navigateur.
* L'import de `backups/ovryk-export-2026-10-01.json` fonctionne : 10 séances, 5 routines, 1RM et 2 cycles de force présents.
* On peut démarrer une séance, la terminer et la retrouver.
* Un cycle en cours avance toujours à la bonne semaine.
* Les données existantes sont inchangées après l'ouverture de la nouvelle version.

## Déploiement et données

* GitHub Pages depuis `https://github.com/ovrykapp/ovryk-app` (branche `main`, racine). Anciennement testé via Netlify Drop.
* Tester d'abord en local (`npx serve -l 8080`) avec l'export importé. Ne jamais publier avant validation locale : une fois en ligne, l'iPhone de Ruben lit directement ses vraies données avec le nouveau code.
* À chaque publication, changer la version du cache dans `sw.js`. Sinon l'iPhone garde l'ancienne interface en cache.
* Les données sont dans le navigateur, propres à l'adresse du site. Elles restent sur l'iPhone tant que l'adresse ne change pas. Ne jamais changer l'adresse de déploiement sans prévenir Ruben, et lui rappeler d'exporter avant.
* En cas de changement d'adresse ou de réinstallation : Profil, Importer (.json), avec le dernier export.
