# Méthode de travail, lot par lot

## Avant un lot

1. Exporte tes données dans Ovryk (Réglages, Exporter) et garde le fichier JSON.
2. Si ce n'est pas déjà fait, crée un dépôt Git dans le dossier du projet (git init) et fais un premier commit. Chaque lot aura son commit.
3. Ouvre le document du lot, relis la section "À faire" et "Critères d'acceptation".

## Pendant un lot

1. Donne à Claude Code le prompt qui figure à la fin du document du lot, et rien d'autre.
2. Demande lui d'abord un plan des modifications, sans rien écrire, et valide le.
3. Une fois le plan validé, il modifie index.html par petites étapes.

## Après un lot

1. Vérifie le script de syntaxe : extraire le script de index.html et lancer node --check.
2. Lance les contrôles automatiques : node outils/verifier-cycles.js, puis python dossier-lots/tests/smoke.py index.html (voir tests/LISEZ-MOI.md).
3. Passe les critères d'acceptation un par un dans un navigateur à 390 x 844.
4. Importe ton export de départ pour vérifier que rien n'est perdu.
5. Augmente la version du cache dans sw.js.
6. Fais le commit du lot, avec le numéro du lot dans le message.
7. Teste sur ton téléphone, application installée.

## Règles

* Un lot à la fois. Si le lot déborde, découpe le, ne l'étends pas.
* Jamais de couleur écrite en dur : utiliser les variables CSS.
* Jamais de changement du format des clés ovryk.* sans migration écrite et testée avec un vrai export.
* Pas de 6 écrit en dur pour la durée d'un cycle : utiliser cycleLength.
* Textes en français, sans emoji, sans tiret long.
* Si une règle de REGLES-METIER.md est ambiguë, s'arrêter et poser la question au lieu de choisir.

## Test de non régression minimal

À la fin de chaque lot, ces six actions doivent fonctionner :

1. Ouvrir chaque onglet sans erreur dans la console.
2. Créer une routine avec un exercice de muscu et un mouvement d'haltérophilie.
3. Démarrer une séance, valider une série, terminer la séance.
4. Voir la séance dans l'historique de l'exercice.
5. Exporter puis importer les données.
6. Fermer et rouvrir l'application : l'état est conservé.
