# LOT 01. Navigation et en-têtes

Taille : S. Dépend de : 00.

## Écrans de la maquette

* ../maquette/01-accueil.png
* ../maquette/04-programme.png
* ../maquette/05-progres.png
* ../maquette/06-fiche-exercice.png
* ../maquette/16-reglages.png

## Objectif

Mettre en place la structure de navigation de la maquette : cinq entrées (Accueil, Programme, Séance au centre, Progrès, Exercices), les Réglages ouverts par une icône, et des titres d'écran à la place de l'en-tête OVRYK.

## Existant à connaître

* Navigation : boutons .nav-btn avec data-target, fonction setActiveView, tableau VIEW_LABELS.
* Section view-routine avec deux sous onglets (Routines et Exercices) gérés par .subnav-btn et data-subtarget (code juste après setActiveView).
* En-tête : balise header.app-header avec le bouton #brand-home-btn et le libellé #current-view-label. L'élément .knurl-strip est déjà masqué.
* Section view-profil : les réglages actuels.

## À faire

1. Barre de navigation : remplacer le bouton data-target="profil" par un bouton data-target="exercices" (libellé Exercices, icône de livre ou de liste). Le bouton Séance reste au centre en orange.
2. Créer la vue exercices : nouvelle section data-view="exercices" id="view-exercices". Y déplacer le contenu de la sous vue Exercices (recherche, filtres de groupe et d'équipement, bouton + Exercice, liste). Les fonctions renderExerciseList, renderExerciseFilters et wireSearchClear ne changent pas, seuls les identifiants parents changent.
3. Simplifier view-routine : supprimer le bloc .routine-subnav, la sous vue Exercices et le code qui gère #view-routine .subnav-btn. Il ne reste que la liste des routines.
4. Réglages : garder la section view-profil et sa clé 'profil'. Ajouter, en haut à droite de l'accueil, un bouton rond (icône engrenage, 44 x 44 px) qui appelle setActiveView('profil'). Dans la barre, aucun onglet n'est actif quand les réglages sont ouverts. Ajouter un bouton de retour dans l'en-tête des réglages.
5. En-tête : supprimer header.app-header, #brand-home-btn et #current-view-label, et le code qui les utilise (clic sur la marque, mise à jour du libellé). Conserver l'espace de la zone de sécurité en haut (safe-area-inset-top). Chaque vue affiche son titre dans .view-header, en Barlow Condensed.
6. Mettre à jour VIEW_LABELS et tous les appels setActiveView qui ciblaient 'routine' pour l'exercice (par exemple depuis les alertes) afin qu'ils pointent vers la bonne vue.
7. Mettre à jour les textes qui citent un onglet (par exemple "onglet Programme" dans l'écran Séance vide).

## Données

Aucune.

## Règles métier concernées

Aucune.

## Critères d'acceptation

* Cinq onglets visibles : Accueil, Programme, Séance (bouton orange), Progrès, Exercices.
* Exercices affiche la bibliothèque avec recherche, filtres et ajout, comme avant.
* Programme n'affiche plus que les routines.
* L'icône engrenage de l'accueil ouvre les réglages, et le retour ramène à l'accueil.
* Plus d'en-tête OVRYK. Les titres d'écran sont visibles et ne passent pas sous l'encoche.
* Fermer et rouvrir l'application ramène sur la dernière vue ouverte, y compris Exercices.
* Aucune erreur dans la console sur les cinq onglets.

## Risques

* Des écouteurs d'événements peuvent supposer que la bibliothèque est dans view-routine : tester la création d'un exercice personnalisé et l'édition du 1RM.
* La mémorisation de la dernière vue (initialTarget) peut contenir 'profil' : vérifier qu'elle fonctionne encore.

## Hors lot

Le contenu de l'accueil (lot 03), l'écran Programme (lot 02) et la fiche exercice (lot 10).

## Prompt pour Claude Code

Copie ce texte dans Claude Code, à la racine du projet, après avoir exporté tes données et fait un commit :

> Lis CLAUDE.md et les documents du dossier dossier-lots : METHODE.md, ETAT-DES-LIEUX.md, MODELE-DE-DONNEES.md, REGLES-METIER.md, puis lots/LOT-01.md et les images de maquette citées. Travaille uniquement sur le lot 01. Commence par me proposer un plan des modifications, sans écrire de code, en citant les fonctions et les identifiants que tu comptes toucher. Attends ma validation. Ensuite modifie index.html par petites étapes, vérifie la syntaxe du script, lance node outils/verifier-cycles.js, teste dans un navigateur à 390 x 844 et passe les critères d'acceptation un par un. Ne touche à rien d'autre. Si une règle est ambiguë, pose moi la question.
