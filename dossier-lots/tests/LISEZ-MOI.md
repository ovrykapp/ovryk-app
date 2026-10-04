# Test de fonctionnement

## Installation, une seule fois

    pip install playwright
    playwright install chromium

## Lancer le test

Depuis la racine du projet (le dossier dossier-lots est posé à côté de index.html) :

    python dossier-lots/tests/smoke.py index.html

Le test ouvre l'application à la taille d'un téléphone, charge des cycles d'exemple (un cycle en semaine 3 sur 8, un en test, un ancien cycle A), ouvre chaque onglet, démarre une séance vide et signale toute erreur. Les captures sont écrites dans tests/captures : regarde les à chaque lot.

## Ce que le test ne vérifie pas

Il ne remplace pas les critères d'acceptation des lots. Il sert à détecter une régression générale. Après chaque lot, passe aussi les critères du lot à la main, avec ton export réel.

## Jeu de données

donnees-exemple.json contient des cycles d'exemple. Si tu changes les identifiants d'exercices, adapte le fichier.
