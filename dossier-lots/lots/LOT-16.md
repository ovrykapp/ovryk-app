# LOT 16. Compte et sauvegarde en ligne

Taille : L. Dépend de : tous.

## Écrans de la maquette

* ../maquette/18-compte-et-sauvegarde.png

## Objectif

Proposer un compte pour sauvegarder automatiquement les données et les retrouver sur un autre appareil, sans jamais gêner l'usage sans compte.

## Existant à connaître

* Toutes les données sont dans le navigateur. Export et import manuels. Application installable avec service worker.

## À faire

1. Choisir le service (décision 9) : Supabase est recommandé.
2. Écran "Compte et sauvegarde" (maquette 18) : connexion avec Google en bouton principal, lien envoyé par e-mail en second, "Plus tard". Pas de connexion avec Apple.
3. Modèle en ligne : une table par type de données (exercices, routines, séances, réglages, cycles) avec l'identifiant de l'utilisateur et une date de modification, accès limité aux données de l'utilisateur.
4. Synchronisation : enregistrer d'abord dans le navigateur, puis envoyer en arrière plan. En cas de conflit, la modification la plus récente gagne, sans jamais supprimer une séance.
5. Première connexion avec des données locales : proposer d'envoyer l'existant. Sur un nouvel appareil : proposer de récupérer.
6. Indicateur d'état dans les réglages ("Synchronisé", "En attente", "Hors ligne").
7. Suppression du compte et des données depuis les réglages.
8. Ne proposer le compte qu'après quelques séances.

## Données

ovryk.sync (état de synchronisation), dates de modification sur chaque entité.

## Règles métier concernées

R11.

## Critères d'acceptation

* Une séance faite sans réseau est envoyée dès que le réseau revient.
* Sur un deuxième appareil, les données se retrouvent après connexion.
* Sans compte, rien ne change.
* La suppression du compte efface les données en ligne.
* Aucune séance n'est perdue en cas de conflit.

## Risques

* Le lot le plus risqué : tester la synchronisation avec un export de départ et deux appareils.
* Les données de santé relèvent du RGPD : suppression sur demande, aucune donnée inutile.
* Ne pas faire ce lot avant que tous les autres soient stables.

## Hors lot

Partage avec un coach, classements.

## Prompt pour Claude Code

Copie ce texte dans Claude Code, à la racine du projet, après avoir exporté tes données et fait un commit :

> Lis CLAUDE.md et les documents du dossier dossier-lots : METHODE.md, ETAT-DES-LIEUX.md, MODELE-DE-DONNEES.md, REGLES-METIER.md, puis lots/LOT-16.md et les images de maquette citées. Travaille uniquement sur le lot 16. Commence par me proposer un plan des modifications, sans écrire de code, en citant les fonctions et les identifiants que tu comptes toucher. Attends ma validation. Ensuite modifie index.html par petites étapes, vérifie la syntaxe du script, lance node outils/verifier-cycles.js, teste dans un navigateur à 390 x 844 et passe les critères d'acceptation un par un. Ne touche à rien d'autre. Si une règle est ambiguë, pose moi la question.
