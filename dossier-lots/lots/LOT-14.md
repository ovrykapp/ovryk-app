# LOT 14. Réglages et matériel

Taille : M. Dépend de : 01.

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

## Prompt pour Claude Code

Copie ce texte dans Claude Code, à la racine du projet, après avoir exporté tes données et fait un commit :

> Lis CLAUDE.md et les documents du dossier dossier-lots : METHODE.md, ETAT-DES-LIEUX.md, MODELE-DE-DONNEES.md, REGLES-METIER.md, puis lots/LOT-14.md et les images de maquette citées. Travaille uniquement sur le lot 14. Commence par me proposer un plan des modifications, sans écrire de code, en citant les fonctions et les identifiants que tu comptes toucher. Attends ma validation. Ensuite modifie index.html par petites étapes, vérifie la syntaxe du script, lance node outils/verifier-cycles.js, teste dans un navigateur à 390 x 844 et passe les critères d'acceptation un par un. Ne touche à rien d'autre. Si une règle est ambiguë, pose moi la question.
