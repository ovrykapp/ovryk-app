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

## Suite de la restauration locale (test_restore_*)

Données fabriquées dans les tests uniquement : jamais d'export réel ni de fichier de backups/. Aucun appel réseau (les polices de l'app sont coupées). Aucune dépendance à git. Les outils communs sont dans restore_commun.py.

Servir le site depuis la racine du projet, puis lancer chaque fichier avec un dossier de travail hors du dépôt :

    python3 -m http.server 8765 --bind 127.0.0.1
    python3 dossier-lots/tests/test_restore_refus.py /tmp/ovryk-tests/refus

Un autre site peut être visé avec la variable OVRYK_URL (c'est ce que fait mutations_restore.py). Chaque fichier commence par un contrôle de l'empreinte : celle des tests doit être égale à celle d'un export produit par l'app sur des données fabriquées, sinon la suite s'arrête.

* test_restore_refus.py : les 17 variantes refusées à l'import (getBackupCrashError), les refus de format, les fichiers acceptés. Les lignes CONSTAT (variante injectée directement : plantage au démarrage ou non) ne comptent pas dans le résultat.
