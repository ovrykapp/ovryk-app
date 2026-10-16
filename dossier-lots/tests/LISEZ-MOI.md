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
* test_restore_ecriture.py : écriture partielle (stockage plein simulé : retour arrière réussi, en échec, ou sur une clé jamais modifiée), IndexedDB muette (abandon à 10 s, horloge simulée, réponse tardive supprimée), copie relue différente, copie impossible.
* test_restore_annulation.py : bandeau de restauration interrompue (retour complet, copie introuvable, Ignorer), libellés Annuler et Rétablir sur un parcours réel, échec d'une annulation, séance en cours, séances perdues comptées par identifiant, 5 copies au plus, abandons, Réglages sans écriture.
* test_restore_reinit.py : Réinitialiser l'app (base de copies, données, marque et copies quotidiennes supprimées, préfixe exact, clés leurres intactes) et base bloquée par un second onglet (suspension à 5 s sur horloge figée, Annuler ou Réinitialiser quand même).
* test_restore_export.py : export et partage refusés pour chacune des 6 clés illisibles, ligne Partager selon le navigateur, partage réussi (fichier valide, lastExportAt noté seulement après le succès, aller-retour par réimport), partage annulé ou en erreur, protection du stockage (partage et navigator.storage simulés).
* test_restore_gardes.py : lecture tolérante d'un exercice de séance sans liste de séries (volume sain inchangé, Accueil sans erreur, 6 clés ovryk.* identiques octet pour octet).
* test_restore_cloud.py : restauration depuis la sauvegarde en ligne, Supabase simulé par des routes Playwright (52 selon LOT-16). Attention : il se termine avec le code de sortie 0 même en cas d'échec (pas de sys.exit). Lire le total « N/52 » en dernière ligne, ne pas se fier au code de sortie.
* Avant de modifier la restauration locale : relancer les 7 fichiers test_restore_*.py (le total de test_restore_cloud.py doit être 52/52), puis mutations_restore.py (environ 12 minutes, dossier de travail hors du dépôt) qui doit afficher 14/14 mutations détectées.
