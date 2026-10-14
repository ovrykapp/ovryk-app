# LOT 16. Sauvegarde en ligne (compte, instantanés, restauration)

Taille : L. Dépend de : tous. Lot à risque (export, import, sauvegardes, écriture dans des données existantes).

Statut : plan révisé le 2026-10-10, décisions de Ruben prises le 2026-10-10 (voir "Décisions prises"). Livraison 1 faite (sw v124), corrigée après quatre audits (sw v125 à v128). Livraison 2 (connexion) faite (sw v129). Livraison 3 (table backups et envoi manuel) faite (sw v130), script SQL à exécuter par Ruben. Livraison 4 (restauration depuis la sauvegarde en ligne) faite (sw v131 et v132, auditée, poussée avec le tag v132-stable). Livraison 5 (envoi automatique après chaque séance) codée (sw v133 et v134), en attente d'audit.

## Écrans de la maquette

* ../maquette/18-compte-et-sauvegarde.png (à adapter, voir section 1 : pas de bouton Google en premier sur iPhone, "synchronisé" devient "sauvegardé").

## Objectif

Ne plus pouvoir perdre l'historique si le téléphone est perdu, réinitialisé, ou si le navigateur efface les données du site. Un seul appareil au quotidien. L'app reste 100 % utilisable sans compte et sans réseau.

## Ce qui change par rapport au cadrage d'origine

Le cadrage d'origine (une table par type de données, synchronisation en arrière plan, "la modification la plus récente gagne", deux appareils) est remplacé par des **instantanés** : une copie complète et datée des données, envoyée sur demande ou après une séance, et une **restauration** volontaire. Raisons :

* Un seul appareil au quotidien : la synchronisation n'apporte rien et ajoute le risque principal (un conflit ou un état vide qui écrase de bonnes données).
* Un instantané complet est cohérent par construction (routines, séances, cycles et réglages de la même minute). Une synchronisation par entité peut mélanger deux états.
* Le format d'un instantané est exactement celui de l'export fichier : on peut quitter le service à tout moment, et la restauration en ligne réutilise la même chaîne que l'import de fichier.
* Les instantanés sont ajoutés, jamais modifiés : une erreur côté app ne peut pas effacer l'historique en ligne.

## État des lieux (lu dans le code, 2026-10-10)

* Données : localStorage, clés ovryk.exercises, ovryk.routines, ovryk.sessions, ovryk.settings, ovryk.forceCycles, ovryk.meta (DB_KEYS). Sauvegardes locales quotidiennes ovryk.backup.AAAA-MM-JJ (routines, exercices, réglages seulement) et ovryk.backup.forceCycles.AAAA-MM-JJ, écrites par migrateSchema au démarrage : **aucune séance n'y est sauvegardée**.
* Export : collectAllOvrykData (format { app, exportedAt, version: 1, data: { exercises, routines, sessions, settings, forceCycles } }, sans ovryk.meta), downloadOvrykExport (fichier JSON indenté). Un export est déclenché automatiquement à chaque fin de séance (finishActiveSession), sans confirmation.
* Import : remplace les cinq clés sans aucun contrôle (un fichier vide ou partiel efface tout), sans copie de l'état actuel avant, sans résumé, sans annulation. Seule protection : une fenêtre de confirmation générique.
* Service worker (sw.js) : met en cache **toute** requête GET réussie, y compris vers un autre domaine. Un appel à un service de sauvegarde serait servi depuis le cache, donc périmé. À corriger avant tout envoi réseau.
* Taille mesurée avec backups/ovryk-export-2026-10-01.json : 206 Ko indenté, environ 126 Ko compact, 19 Ko compressé. 10 séances = 56 Ko, soit 5,6 Ko par séance en moyenne (6,5 Ko au plus). Exercices 51 Ko, routines 19 Ko, réglages et cycles moins de 1 Ko.
* Projection : 4 séances par semaine, environ 1,2 Mo de séances par an. **Le localStorage de Safari est limité à environ 5 Mo par site** : le plafond serait atteint en 3 à 4 ans. Hors de ce lot, mais à noter (section 11).

## 1. Authentification

Recommandation : **code à 6 chiffres reçu par e-mail** (connexion sans mot de passe par code, "OTP"), saisi dans l'app.

* Pourquoi pas le lien magique : sur iPhone, un lien reçu par e-mail s'ouvre dans Safari, jamais dans l'app installée, et l'app installée a un stockage séparé de Safari. La session serait ouverte dans Safari et pas dans l'app. Le code évite tout lien et toute redirection : tout se passe dans l'app.
* Pourquoi pas Google en premier (maquette) : la connexion Google passe par une redirection vers google.com puis un retour. Dans une app installée sur iPhone, le retour atterrit souvent dans Safari ou dans une fenêtre intégrée, pas dans l'app (hypothèse forte, non testée ici, voir "certain ou hypothèse"). À garder pour plus tard, pas dans ce lot.
* Mot de passe : possible (pas d'e-mail à chaque connexion), mais un mot de passe de plus à retenir et à protéger. Alternative acceptable si Ruben préfère (question 2).
* Durée de session : jeton d'accès court (environ 1 heure) renouvelé automatiquement par un jeton de renouvellement gardé sur l'appareil. On ne se reconnecte que si l'app perd ses données (justement le cas où l'on veut restaurer) ou après une déconnexion.
* Comptes : un seul compte. Après la création du compte de Ruben, **désactiver les nouvelles inscriptions** dans le service, pour que personne d'autre ne puisse créer un compte avec la clé publique et consommer le quota gratuit.

## 2. Contenu sauvegardé

Sauvegardé dans chaque instantané :

* ovryk.exercises, ovryk.routines, ovryk.sessions (y compris la séance en cours si elle existe, avec son statut in_progress), ovryk.settings, ovryk.forceCycles, ovryk.meta (version de schéma).

Exclu :

* ovryk.backup.* (copies locales, redondantes avec l'instantané).
* Les nouvelles clés du lot : état de la sauvegarde (ovryk.cloud) et jetons de connexion (ovryk.cloud.auth). Un jeton ne doit jamais partir dans un instantané ni dans un export fichier.
* Les caches du service worker et le point de restauration local.
* Dans ovryk.settings : rien n'est exclu. lastExportAt et les préférences sont utiles à la restauration.

Taille d'un instantané aujourd'hui : environ 126 Ko compact. Avec 500 séances (2 ans et demi) : environ 3 Mo. Compression possible plus tard (gain d'un facteur 6 à 10 mesuré), pas nécessaire au départ.

## 3. Format

Recommandation : **reprendre le format d'export existant**, en restant lisible par l'import actuel.

* Enveloppe : { app: 'Ovryk', exportedAt, version: 1, data: { exercises, routines, sessions, settings, forceCycles, meta }, summary }. L'import actuel lit parsed.data et ignore ce qu'il ne connaît pas : un fichier au nouveau format reste importable par une ancienne version.
* summary (nouveau, lecture humaine et garde-fous) : nombre de séances terminées et au total, identifiants des séances en cours, date de la dernière séance terminée, nombre de routines, d'exercices et de cycles, version de schéma, empreinte (somme de contrôle) du contenu de data. Pas de version de l'app : ce serait un deuxième numéro à tenir à jour à côté de sw.js, et la version de schéma suffit à refuser une sauvegarde trop récente.
* meta.schemaVersion indique la version du modèle. À la restauration, un instantané d'une version plus récente que l'app est refusé avec un message ("Mets à jour l'app avant de restaurer"). Un instantané plus ancien est accepté et passe par migrateSchema.
* Côté service : une ligne par instantané, avec l'identifiant du compte, la date, le résumé en colonnes (pour lister sans tout télécharger) et le contenu complet en un seul champ JSON.

## 4. Quand sauvegarder

Recommandation :

* **Manuel** : bouton "Sauvegarder maintenant" dans Réglages.
* **Automatique après chaque séance terminée**, si la sauvegarde en ligne est activée (même moment que l'export fichier actuel, une action de l'utilisateur).
* **Pas d'envoi à l'ouverture de l'app** (règle "rien n'est écrit à l'ouverture") et pas de minuterie quotidienne : une PWA iPhone ne tourne pas en arrière plan, un envoi "quotidien" ne serait de toute façon pas fiable.
* Rappel visible, en lecture seule : si la dernière sauvegarde réussie a plus de 7 jours, Réglages et l'Accueil l'affichent.

Hors ligne et échecs :

* Si l'envoi échoue (pas de réseau, service en pause, session expirée), l'état passe à "En attente" avec la raison et l'heure. Le contenu n'est pas mis en file : au prochain essai, c'est l'état du moment qui est envoyé, plus complet par définition.
* Nouvel essai : à la prochaine fin de séance, au bouton manuel, et quand le réseau revient pendant que l'app est ouverte (événement "online").
* Échec silencieux interdit : Réglages affiche toujours "Dernière sauvegarde réussie : date, N séances" et, s'il y en a une, la dernière erreur en clair. Après une séance, un message court dit "Sauvegarde envoyée" ou "Sauvegarde en attente : pas de réseau".

## 5. Restauration

* **Jamais sans confirmation explicite**, sur un écran dédié.
* **Résumé avant et après** : date de l'instantané, nombre de séances, de routines et de cycles, date de la dernière séance, à côté des mêmes chiffres sur l'appareil. Si l'instantané contient **moins de séances** que l'appareil, avertissement rouge et deuxième confirmation.
* **Point de restauration local automatique** juste avant de remplacer : copie complète de l'état actuel, séances comprises. Recommandation : le stocker dans IndexedDB plutôt que dans localStorage (une deuxième copie complète doublerait l'occupation et rapprocherait du plafond de 5 Mo). En complément, si la sauvegarde en ligne est active, un instantané "avant restauration" est envoyé avant de remplacer.
* **Annulation** : bouton "Annuler la dernière restauration" dans Réglages, qui remet le point de restauration (avec la même confirmation).
* **Remplacer ou fusionner : recommandation "Remplacer", avec point de restauration et annulation.** Raisons : un instantané est cohérent, alors qu'une fusion de routines, de cycles (semaine en cours, 1RM) et de réglages produit des états qu'aucun des deux appareils n'a jamais eus, et une séance peut avoir été modifiée des deux côtés. Option possible plus tard, limitée et sûre : "ajouter seulement les séances absentes" (par identifiant, sans jamais modifier ni supprimer), pour récupérer des séances d'un vieil instantané sans revenir en arrière sur le reste.
* La même chaîne sert à l'import de fichier : l'import actuel gagne la validation, le résumé, le point de restauration et l'annulation (livraison 1).
* Validation avant de toucher à quoi que ce soit : structure attendue, tableaux bien formés, empreinte qui correspond, version de schéma acceptée. Un instantané invalide n'est jamais appliqué.

## 6. Historique des instantanés

Recommandation : rotation faite **côté service**, l'app ne peut qu'ajouter et lire.

* On garde : les 10 plus récents, plus un par semaine sur 8 semaines, plus un par mois sur 12 mois, plus **toujours l'instantané qui contient le plus de séances**.
* Ordre de grandeur : une trentaine d'instantanés au plus, environ 100 Mo avec 3 Mo chacun, sous la limite de 500 Mo.
* Garde-fous contre une sauvegarde d'un état vide :
  * Côté app : pas d'envoi si l'appareil a 0 séance terminée alors que le dernier instantané en ligne en avait au moins une. Message "Rien à sauvegarder : cet appareil semble vide. Veux-tu restaurer ?".
  * Côté app : si le nombre de séances baisse par rapport au dernier instantané, l'envoi reste possible mais l'instantané est marqué "en baisse" et le message le dit.
  * Côté service : la rotation ne supprime jamais l'instantané le plus complet. Comme un instantané n'est jamais remplacé, un état vide ou corrompu ne peut pas écraser le seul bon.

## 7. Sécurité et données personnelles

* **Règles d'accès par ligne (RLS)** activées sur la table : un compte ne peut lire et ajouter que ses propres lignes. Ni modification ni suppression autorisées depuis l'app.
* La rotation et "Supprimer mes sauvegardes en ligne" passent par deux fonctions côté service qui n'agissent que sur les lignes du compte connecté.
* Clés :
  * La **clé publique** ("publishable", ou "anon" sur les anciens projets) est faite pour être visible dans le navigateur ; la sécurité repose sur RLS. Elle peut figurer dans index.html (question 3).
  * La **clé secrète** ("secret" ou "service_role") contourne RLS. Elle ne doit jamais apparaître dans index.html, dans le dépôt, ni dans un message.
* **Inscriptions désactivées** une fois le compte de Ruben créé (section 1).
* **Région** : Europe, Paris si proposée, sinon Francfort.
* **Données** : séances, charges, réglages, adresse e-mail. Pas de nom, pas de poids corporel. Usage personnel.
* **Suppression** :
  * Bouton "Supprimer mes sauvegardes en ligne" (confirmation en deux temps, supprime toutes les lignes du compte).
  * Pour tout effacer, compte compris : supprimer le projet depuis le tableau de bord du service (étape documentée).
* **Mise en pause du projet gratuit** : après 7 jours sans activité, avec un e-mail d'avertissement avant. Le projet reste restaurable pendant 90 jours depuis le tableau de bord.
  * Pendant la pause, l'envoi échoue et l'app l'affiche ("Service en pause, ouvre le tableau de bord pour le réactiver"). Les données locales ne sont pas touchées.
  * Une séance par semaine suffit à éviter la pause.
  * Risque réel : une longue pause d'entraînement de plus de 90 jours pendant laquelle le téléphone est perdu.
* Le service n'offre **aucune sauvegarde automatique de la base** sur l'offre gratuite : les instantanés en ligne sont la seule copie hors de l'appareil. L'export fichier (vers Fichiers ou iCloud Drive) reste donc utile comme deuxième filet.

## 8. Intégration technique

* **Sans bibliothèque** : appels HTTP simples (fetch, ES5) vers les deux interfaces du service, connexion et table. Pas de SDK de 50 Ko à charger, rien à ajouter au démarrage.
* **Service worker** : le gestionnaire fetch ne traite plus que les requêtes **du même domaine**. Toute requête vers le service (connexion, lecture, envoi) passe directement au réseau, jamais en cache. Un appel en cours de connexion ou un jeton ne doivent jamais être mis en cache. Version de cache augmentée à cette livraison.
* **CORS** : l'interface du service accepte les appels depuis un autre domaine avec la clé publique (hypothèse documentée, à vérifier en livraison 2 depuis ovrykapp.github.io).
* **CSP** : la page n'en déclare pas aujourd'hui. Si on en ajoute une, connect-src doit inclure l'adresse du projet.
* **Chargement** : aucun appel réseau au démarrage, aucun script externe ajouté, aucune écriture.
* **Sans compte ou sans réseau**, l'app fonctionne exactement comme aujourd'hui. L'état de la sauvegarde ne s'affiche que dans Réglages, et dans l'Accueil en cas d'échec.
* **Délai d'attente** : 20 secondes par appel, une seule requête à la fois, bouton désactivé pendant l'envoi.
* **Données conservées sur l'appareil** :
  * ovryk.cloud : activé, dernière réussite (date, nombre de séances, identifiant de l'instantané), dernière erreur (date, raison).
  * ovryk.cloud.auth : jetons.
  * Point de restauration dans IndexedDB.
  * Ces clés ne sont pas exportées et sont effacées par "Se déconnecter".
* **Persistance du stockage** : demander navigator.storage.persist() (Safari 17 et plus) sur une action de Ruben dans Réglages ("Protéger les données de cet appareil"). Safari accorde ce mode plus facilement à une app installée, et les données d'un site en mode persistant sont exclues de l'effacement automatique.
* **Règle 14** (écritures de routine dans l'éditeur) : ce lot n'écrit dans les routines que par la restauration, qui remplace tout d'un bloc puis recharge l'app. Aucune écriture depuis l'éditeur, donc pas de copie partagée périmée possible (routineEditorLive). La restauration ne doit jamais être proposée pendant que l'éditeur de routine est ouvert.

## 9. Ce que Ruben fait lui-même (étapes, dans l'ordre)

À faire seulement après les décisions de la section 12, et seulement au moment de la livraison 2.

1. Aller sur supabase.com, "Start your project", créer un compte (avec GitHub ou une adresse e-mail).
2. "New project" : nom ovryk, mot de passe de base de données généré (le garder dans le gestionnaire de mots de passe, l'app n'en a pas besoin), région Europe (Paris ou Francfort), offre Free.
3. Attendre la fin de la création (1 à 2 minutes).
4. Menu Authentication, puis Sign In / Providers : vérifier que Email est activé.
5. Menu Authentication, puis Emails, modèle "Magic Link" : remplacer le texte par une phrase contenant le code, par exemple "Ton code Ovryk : {{ .Token }}" (texte exact fourni à la livraison 2). Enregistrer.
6. Menu SQL Editor : coller le script fourni à la livraison 3 (table, règles d'accès, rotation, fonction de suppression), cliquer Run, vérifier "Success".
7. Menu Project Settings, puis API Keys (ou API) : copier l'adresse du projet (Project URL, du type https://xxxx.supabase.co) et la clé publique (publishable, ou anon). Les envoyer pour qu'elles soient mises dans l'app. **Ne jamais copier ni envoyer la clé secrète** (secret ou service_role).
8. Dans l'app (après la livraison 2) : Réglages, Sauvegarde en ligne, saisir son e-mail, recevoir le code, le saisir.
9. Revenir dans Authentication, Sign In / Providers, et désactiver "Allow new users to sign up". Le compte existant continue de fonctionner.
10. Garder l'e-mail d'avertissement de mise en pause en tête : s'il arrive, ouvrir le tableau de bord du projet suffit à le relancer.

## 10. Livraisons

Chaque livraison a son commit, une version de cache et ses tests sur la copie locale avec l'export de backups/. Toutes les livraisons de ce lot sont à risque. Celles qui demandent un **audit Opus avant push** sont indiquées.

1. **Export fiable et restauration sûre depuis un fichier, sans réseau.**
   * Export au nouveau format (meta et summary, compact).
   * Bouton "Partager la sauvegarde" (feuille de partage iPhone, vers Fichiers ou iCloud Drive).
   * Import réécrit sur une chaîne unique : valider, résumer avant et après, point de restauration IndexedDB, remplacer, annuler. Refus d'un fichier vide ou invalide. Avertissement si moins de séances.
   * "Protéger les données de cet appareil" (persist).
   * Risque : moyen, l'import touche toutes les données.
   * Écrit : point de restauration (IndexedDB), données remplacées seulement après confirmation.
   * Tests : aller-retour export et import identique, fichier vide refusé, fichier ancien format accepté, annulation qui remet l'état exact, aucune écriture à l'ouverture.
   * **Audit Opus avant push.**
2. **Connexion, sans envoi de données.**
   * Correction du service worker (même domaine seulement).
   * Configuration du projet.
   * Écran "Sauvegarde en ligne" dans Réglages : saisie de l'e-mail, du code, état connecté, déconnexion. Aucune donnée d'entraînement envoyée.
   * Risque : moyen (jetons, service worker).
   * Écrit : ovryk.cloud.auth à la connexion seulement.
   * Tests : connexion, renouvellement du jeton, déconnexion, mode avion, aucun appel réseau sans action, aucune réponse du service en cache.
   * **Audit Opus avant push.**
3. **Sauvegarde manuelle et liste des instantanés.**
   * Script SQL fourni à Ruben : table, règles d'accès, rotation, garde du plus complet, fonction de suppression.
   * "Sauvegarder maintenant", garde-fous contre l'état vide ou en baisse.
   * État visible, liste des instantanés (date, séances).
   * Risque : moyen.
   * Écrit : ovryk.cloud (état), une ligne en ligne par envoi.
   * Tests : envoi, refus d'un état vide, état d'erreur visible, mode avion, service injoignable, lecture interdite des lignes d'un autre compte (vérifié avec un deuxième compte de test, puis supprimé).
   * **Audit Opus avant push.**
4. **Sauvegarde automatique après une séance.**
   * Envoi à la fin d'une séance si la sauvegarde est activée.
   * Nouvel essai au retour du réseau, messages "envoyée" ou "en attente".
   * Choix sur l'export fichier automatique actuel (question 8).
   * Risque : moyen.
   * Tests : séance terminée en ligne puis hors ligne, retour du réseau, jeton expiré, service en pause simulé.
   * **Audit Opus avant push.**
5. **Restauration depuis un instantané en ligne, et suppression des sauvegardes.**
   * Réutilise la chaîne de la livraison 1, plus un instantané "avant restauration" envoyé d'abord.
   * "Supprimer mes sauvegardes en ligne".
   * Risque : élevé, la restauration remplace toutes les données.
   * Tests : restauration complète sur une copie vierge (téléphone neuf simulé), restauration d'un instantané plus ancien avec avertissement, annulation, refus d'un instantané corrompu ou d'une version plus récente, suppression en ligne.
   * **Audit Opus avant push.**
6. (Plus tard, optionnel) "Ajouter les séances absentes" depuis un instantané, sans rien modifier ni supprimer.

## 11. Risques, du plus grave au moins grave

1. **Restauration qui écrase de bonnes données par de vieilles.** Parades : résumé avant et après, avertissement si moins de séances, double confirmation, point de restauration local, instantané "avant restauration" en ligne, annulation.
2. **Perte silencieuse : on croit être sauvegardé alors que l'envoi échoue** (pause, jeton expiré, réseau). Parades : état toujours visible avec la date de la dernière réussite, rappel au-delà de 7 jours, message après chaque séance, jamais de "réussi" sans réponse positive du service.
3. **Sauvegarde d'un état vide ou corrompu** (téléphone neuf, données effacées) qui ferait croire que tout est perdu. Parades : refus côté app, instantanés jamais remplacés, rotation qui garde toujours le plus complet.
4. **Réponses du service en cache dans le service worker** : une restauration recevrait une vieille copie. Parade : correction du service worker en livraison 2, avant tout appel.
5. **Projet gratuit en pause plus de 90 jours**, ou changement des conditions de l'offre gratuite. Parades : l'export fichier reste disponible et rappelé, format ouvert, contenu récupérable depuis le tableau de bord tant que le projet existe.
6. **Fuite de la clé secrète** dans le dépôt. Parade : elle n'est jamais demandée ni utilisée par l'app, vérification par recherche dans le dépôt à chaque audit.
7. **Quelqu'un d'autre crée un compte** avec la clé publique et consomme le quota. Parade : inscriptions désactivées, règles d'accès par ligne.
8. **Verrouillage sur un service** : faible. Le contenu est le JSON d'export, lisible et réimportable sans le service.
9. **Plafond du localStorage (environ 5 Mo)** atteint dans 3 à 4 ans au rythme actuel. Hors lot, à prévoir : déplacer les séances vers IndexedDB (lot à part).
10. **Limite d'e-mails** (2 par heure avec l'envoi intégré) : suffisant pour un seul utilisateur. Un code redemandé trop vite échoue avec un message clair.

Hors de ce lot : synchronisation entre plusieurs appareils, connexion Google ou Apple, import depuis Hevy ou Strong, partage avec un coach, fusion complète de deux états, chiffrement côté app avant envoi (possible plus tard ; il protège même contre le service, mais une phrase secrète perdue rend les sauvegardes illisibles), migration du stockage vers IndexedDB.

## Décisions prises (2026-10-10)

* Service : Supabase, offre gratuite (question 1, A).
* Connexion : code à 6 chiffres reçu par e-mail (question 2, A). **Remplacée le 2026-10-14 : e-mail et mot de passe** (compte unique créé à la main, inscriptions publiques désactivées), voir "Avancement", livraison 2.
* Adresse du projet et clé publique : directement dans l'app (question 3, A).
* Restauration : remplacer, avec copie de l'état actuel avant et annulation (question 4, A).
* Quand : après chaque séance terminée, plus un bouton manuel (question 5, A).
* Rotation (remplace la règle de la section 6) : **les 30 dernières sauvegardes, plus toujours la plus complète** (celle qui contient le plus de séances terminées).
  * Taille réelle mesurée avec backups/ovryk-export-2026-10-01.json au nouveau format compact (avec meta et summary) : **114 Ko par copie** (18 Ko compressée), environ 5 Ko par séance.
  * 31 copies aujourd'hui : 3 Mo. Après 1 an (environ 220 séances) : 35 Mo. Après 3 ans : environ 100 Mo. Après 10 ans : environ 320 Mo, sous la limite de 500 Mo.
  * La règle ne pose donc aucun problème de place. Le stockage local du téléphone (environ 5 Mo) sera saturé bien avant, vers 5 ans, ce qui reste le vrai plafond (section 11, risque 9).
* Export fichier automatique en fin de séance (question 8) : **conservé au moins un mois après l'activation de la sauvegarde en ligne**, puis réévalué.
* Région : non tranchée explicitement, recommandation Paris si proposée, sinon Francfort (à choisir à la création du projet).

## 12. Décisions pour Ruben (questions posées le 2026-10-10, réponses ci-dessus)

1. **Où mettre la sauvegarde en ligne ?**
   * A (recommandé) : Supabase, offre gratuite. Fait ce qu'il faut sans serveur à nous, les données restent lisibles, région Europe.
   * B : seulement un fichier envoyé vers Fichiers ou iCloud Drive après chaque séance (aucun compte, aucun service, mais il faut le faire à la main à chaque fois).
   * C : Firebase. Pas de mise en pause, mais un document est limité à 1 Mo (une sauvegarde dépassera cette taille en 1 à 2 ans), et la connexion par code e-mail n'existe pas : il faudrait un mot de passe.
   * Dans tous les cas, l'option B arrive en livraison 1, comme filet supplémentaire.
2. **Comment te connecter sur l'iPhone ?**
   * A (recommandé) : un code à 6 chiffres reçu par e-mail, saisi dans l'app. Pas de mot de passe, rien qui s'ouvre dans Safari.
   * B : e-mail et mot de passe.
   * C : Google. Déconseillé sur une app installée sur iPhone, le retour de connexion tombe souvent dans Safari.
3. **Où ranger l'adresse du projet et la clé publique ?**
   * A (recommandé) : directement dans l'app. La clé publique n'est pas un secret et la sécurité vient des règles d'accès.
   * B : tu les saisis dans Réglages. Rien dans le code, mais à ressaisir si l'app perd ses données, c'est à dire au moment précis où tu veux restaurer.
4. **Restaurer, c'est remplacer ou fusionner ?**
   * A (recommandé) : remplacer, avec copie de l'état actuel juste avant et bouton d'annulation.
   * B : fusionner. Plus risqué : on peut obtenir un mélange qu'aucun téléphone n'a jamais eu.
   * Plus tard, une option "ajouter seulement les séances absentes".
5. **Quand sauvegarder ?**
   * A (recommandé) : après chaque séance terminée, plus un bouton.
   * B : seulement le bouton.
   * Une sauvegarde "tous les jours" n'est pas fiable sur iPhone (l'app ne tourne pas en arrière plan).
6. **Combien d'anciennes sauvegardes garder ?**
   * A (recommandé) : les 10 dernières, une par semaine sur 2 mois, une par mois sur un an, et toujours la plus complète.
   * B : toutes, au risque d'atteindre la limite gratuite dans quelques années.
7. **Région** : A (recommandé) Paris si proposée, sinon B Francfort.
8. **L'export fichier automatique à chaque fin de séance** (il existe déjà) :
   * A (recommandé) : le garder tant que la sauvegarde en ligne n'est pas active, puis le remplacer par la sauvegarde en ligne (export à la demande seulement).
   * B : toujours le garder.

## Certain ou hypothèse

Vérifié dans la documentation officielle le 2026-10-10 :
* Offre gratuite Supabase (page tarifs) : base de 500 Mo, 1 Go de fichiers, 5 Go de trafic sortant, 50 000 utilisateurs actifs par mois, 2 projets actifs, aucune sauvegarde automatique, pause après 1 semaine d'inactivité.
* Projet en pause : e-mail d'avertissement, restaurable pendant 90 jours (documentation "Project Pausing" et journal des changements).
* Connexion par code e-mail : le modèle d'e-mail utilise {{ .Token }}, un code toutes les 60 secondes au plus, code valable 1 heure par défaut. Envoi intégré limité à 2 e-mails par heure (documentation "Rate limits").
* Clé publique faite pour être visible, sécurité par les règles d'accès par ligne ; la clé secrète contourne ces règles (documentation et guides de sécurité).
* WebKit, politique de stockage : une app installée sur l'écran d'accueil a son propre compteur de jours et son stockage n'est pas effacé tant qu'elle est utilisée ; navigator.storage.persist() existe depuis Safari 17, accordé selon des heuristiques (dont le fait d'être une app installée) ; un site en mode persistant est exclu de l'effacement automatique ; la politique couvre localStorage (blog WebKit "Updates to Storage Policy" et "Full Third-Party Cookie Blocking and More").
* Stockage séparé entre Safari et l'app installée, et lien d'e-mail qui s'ouvre dans Safari : bogue WebKit 181849 et retours concordants.

Hypothèses, à vérifier pendant les livraisons :
* Le retour d'une connexion Google dans une app installée sur iPhone atterrit hors de l'app (largement rapporté, non testé ici).
* La région Paris est proposée à la création du projet (Francfort l'est à coup sûr).
* L'interface du service accepte les appels depuis ovrykapp.github.io sans réglage (CORS), et la taille d'une requête de quelques Mo passe.
* Les noms exacts des menus du tableau de bord (ils changent souvent) : les étapes de la section 9 seront relues au moment de la livraison 2.
* Le plafond de 5 Mo du localStorage de Safari (valeur couramment observée, pas une garantie écrite).
* Firebase : limite de 1 Mo par document et quotas gratuits (sources secondaires), et le fait qu'aucune mise en pause n'existe (non trouvé dans la documentation).

Sources : https://supabase.com/pricing , https://supabase.com/docs/guides/platform/free-project-pausing , https://supabase.com/changelog/27497-paused-free-plan-projects-are-restorable-for-90-days , https://supabase.com/docs/guides/auth/auth-email-passwordless , https://supabase.com/docs/guides/auth/rate-limits , https://supabase.com/docs/guides/platform/backups , https://webkit.org/blog/14403/updates-to-storage-policy/ , https://webkit.org/blog/10218/full-third-party-cookie-blocking-and-more/ , https://bugs.webkit.org/show_bug.cgi?id=181849

## Critères d'acceptation (lot entier)

* Sans activer la sauvegarde en ligne, rien ne change et aucun appel réseau n'est fait.
* Une séance terminée avec la sauvegarde active apparaît dans un nouvel instantané, ou l'état "En attente" est visible avec la raison.
* Sur une copie vierge (téléphone neuf simulé), la restauration retrouve exactement l'export de départ.
* Un état vide n'efface jamais un instantané en ligne.
* Toute restauration peut être annulée.
* Aucune clé secrète dans le dépôt.

## Règles métier concernées

R11 (pas de compte obligatoire).

## Avancement

* Livraison 1 faite le 2026-10-10 (sw v124), sans réseau ni dépendance :
  * Export : collectAllOvrykData ajoute data.meta et summary (empreinte FNV-1a de data, hashBackupString). Même enveloppe version 1, toujours lisible par l'ancien import. Garde de sortie getBackupBlocker : pas d'export (ni bouton, ni export automatique de fin de séance, ni partage) d'un état vide ou illisible, avec message ; l'export automatique de fin de séance est inchangé (il ne peut pas être bloqué juste après une séance terminée).
  * Partage : ligne "Partager une sauvegarde" (feuille de partage, Fichiers ou iCloud Drive), affichée seulement si le navigateur sait partager un fichier ; note lastExportAt seulement si le partage aboutit.
  * Import : validateBackupFile refuse sans rien écrire un fichier vide, du JSON illisible, un autre format, une autre application, une version d'enveloppe inconnue, un schéma plus récent, une empreinte différente (fichier abîmé ou modifié), des listes absentes ou invalides, des données vides. L'ancien format brut (listes à la racine) et l'export réel du 2026-10-01 (sans meta ni summary) restent acceptés. Un élément isolé mal formé n'est pas un refus (il est signalé).
  * Écran "Restaurer une sauvegarde" (restore-page) : comparaison "Ce téléphone" et "Sauvegarde" (séances terminées, dernière séance, routines, exercices, cycles), avertissement rouge si la sauvegarde a moins de séances terminées, ou si une séance en cours sur le téléphone n'y est pas. Double confirmation (bouton, puis fenêtre qui rappelle les séances perdues).
  * Copie avant restauration : les six clés ovryk.* en valeurs brutes (séances comprises), dans IndexedDB (base ovryk-restore, 5 copies au plus). Si la copie échoue, rien n'est remplacé. Si une écriture échoue pendant le remplacement, l'état d'avant est remis à l'identique.
  * Annulation : ligne "Annuler la dernière restauration" (visible seulement s'il existe une copie, lue sans créer la base), même écran, même double confirmation ; l'annulation fait elle-même une copie, elle est donc annulable.
  * "Protéger les données de cet appareil" : navigator.storage.persist() sur un appui, état affiché (Activée ou Non activée), ligne masquée si le navigateur ne le propose pas.
  * Aucune écriture à l'ouverture de Réglages (ni localStorage, ni création de base IndexedDB). Aucune migration, aucune nouvelle clé dans localStorage.
  * À savoir : restaurer un fichier remet aussi son lastExportAt, qui est celui d'avant l'export (la date d'export est notée après la préparation du fichier). Le rappel "dernière sauvegarde il y a N jours" peut donc réapparaître après une restauration.
* Reste pour la livraison 2 : correction du service worker (même domaine seulement), configuration du projet (adresse et clé publique dans l'app), connexion par code e-mail (saisie de l'e-mail, du code, renouvellement du jeton, déconnexion) dans un écran "Sauvegarde en ligne" des Réglages, ovryk.cloud.auth, sans aucun envoi de données d'entraînement. Étapes manuelles de Ruben 1 à 5 et 7 de la section 9 au même moment.
* Corrections après l'audit de la livraison 1 (sw v125), toujours sans réseau :
  1. Import : refus, sans rien écrire, des fichiers qui feraient planter le démarrage (getBackupCrashError). 17 variantes testées sur v124, toutes plantaient au lancement, et 6 rendaient Réglages, donc l'annulation, inaccessibles. Cas refusés :
     * exercice du catalogue vide ou sans identifiant ;
     * routine vide, sans identifiant ou sans liste d'exercices, exercice de routine vide ou sans séries ;
     * séance vide, sans identifiant, sans date valide ou sans liste d'exercices, exercice de séance vide ou sans séries, série vide ;
     * valeur de forceCycles qui n'est pas un objet, ou cycle vide ou d'un type inconnu.
     L'export réel du 2026-10-01 et un export de l'app (séance en cours, routine en création sans exercice, exercice personnalisé sans historique, cycle en attente de validation) restent acceptés. La mention "éléments mal formés importés tels quels" est supprimée.
  2. Retour arrière : writeRawOvrykState réécrit les clés les plus petites d'abord et sa valeur est vérifiée. S'il échoue, le message dit "Restauration interrompue : utilise Annuler la dernière restauration", sans rechargement, et la marque reste posée.
  3. Séances perdues comptées par identifiant (getMissingCompletedSessionIds), à l'écran et dans la deuxième confirmation, pour un fichier comme pour une annulation : une séance faite depuis la restauration est signalée, et "même nombre mais séances différentes" aussi.
  4. Export et partage refusés si l'une des six clés ovryk.* est présente mais illisible (avant, l'export sortait sans les séances avec "Export téléchargé").
  5. La copie est relue par son identifiant et comparée à l'état courant avant toute écriture ; en cas de différence, rien n'est remplacé.
  6. Marque ovryk.restoreInProgress posée juste avant le remplacement, retirée juste avant le rechargement (et après un retour arrière réussi). Au lancement, si elle existe, bandeau "Restauration interrompue" sur l'Accueil : "Revenir à la copie d'avant" (même écran, même double confirmation) ou "Ignorer" (après confirmation). Aucune écriture automatique.
  7. Le nettoyage des vieilles copies est fait à part, après coup, erreurs ignorées : il ne bloque plus une restauration.
  8. Plus de délai de 600 ms : l'écran est bloqué et la page rechargée tout de suite.
  9. Libellé : après une annulation, la ligne de Réglages et l'écran disent "Rétablir la restauration" (la copie la plus récente a été faite avant une annulation) ; après un rétablissement, de nouveau "Annuler".
* Seconde correction après l'audit de fe0773b (sw v126), sans réseau et sans changer aucune règle d'acceptation ou de refus d'un fichier :
  1. IndexedDB qui ne répond jamais : la restauration est abandonnée après 10 secondes (RESTORE_COPY_TIMEOUT_MS) avec "La copie de sécurité n'a pas pu être faite, rien n'a été remplacé". L'écran est débloqué, aucune donnée n'est touchée, et une réponse tardive est ignorée.
  2. "Réinitialiser l'app" retire aussi la marque ovryk.restoreInProgress. Si la copie est introuvable, "Revenir à la copie d'avant" le dit dans le bandeau même (showRestoreBannerCopyMissing) : le bouton est masqué, il ne reste que "Ignorer", et la phrase "la copie est sur ce téléphone" est retirée.
  3. Refus "sans identifiant" : la règle est identique, mais le message est devenu exact. Il ne dit plus que l'app ne démarrerait pas (vérifié : un élément sans identifiant ne la fait pas planter). Les autres refus gardent la mention.
  4. Après une restauration ratée puis remise en état, la ligne de Réglages n'apparaît plus : elle est masquée quand la copie la plus récente est identique à l'état actuel (lecture seule).
  5. Échec d'une annulation ou d'un rétablissement : le message cite le libellé réellement affiché (restoreRowLabel, partagé avec la ligne).
  6. Cas limite trouvé en testant : si le retour arrière échoue sur une clé jamais modifiée, l'état est en fait intact. L'app dit alors "rien n'a changé" et retire la marque, au lieu de renvoyer vers une ligne masquée.
* Troisième correction après l'audit de 4bc1427 (sw v127), sans réseau et sans changer aucune règle d'acceptation d'un fichier :
  1. "Réinitialiser l'app" supprime d'abord la base de copies de restauration (deleteRestoreDb, délai RESET_DB_TIMEOUT_MS de 5 secondes), puis les données, la marque et recharge (wipeAppDataAndReload). Le texte de confirmation mentionne les copies. Si la suppression de la base échoue ou ne répond pas, rien n'est encore supprimé et l'app le dit, puis propose "Réinitialiser quand même" en précisant que les copies resteront, ou "Annuler".
  2. La ligne "Annuler" ou "Rétablir" propose la copie la plus récente QUI DIFFÈRE de l'état actuel (getUndoCandidatePoint, lecture seule), et l'écran d'annulation utilise la même fonction (openRestoreUndo, openRestorePageFromPoint). Une tentative ratée puis remise en état ne masque plus l'annulation d'une vraie restauration. Si toutes les copies sont identiques à l'état actuel, la ligne reste masquée.
  3. Une copie arrivée après l'abandon à 10 secondes, ou relue différente de l'état actuel, est supprimée dès son arrivée (discardRestorePoint), sans aucune écriture dans les clés ovryk.*. Plus de ligne "Annuler" fantôme.
* Quatrième correction après l'audit de 8fae8a6 (sw v128), sans réseau et sans changer aucune règle d'acceptation d'un fichier :
  1. "Réinitialiser l'app" supprime aussi les copies quotidiennes (wipeAppDataAndReload), filtrées sur le préfixe exact "ovryk.backup." (dont "ovryk.backup.forceCycles."), jamais sur "ovryk." seul : une clé comme ovryk.cloud.auth n'est pas touchée. Ordre : base de copies, clés de données, marque, copies quotidiennes, rechargement. Le texte de confirmation devient vrai. L'app recrée au démarrage suivant les copies du jour, à partir de l'état vide (vérifié : aucune routine de l'ancien état).
  2. Une tentative de restauration remise en état supprime la copie qu'elle avait créée (deleteRestorePointById, réutilise discardRestorePoint) : elle ne devient plus "la copie à annuler", et la copie de la restauration précédente reste proposée, y compris après une nouvelle séance.
  3. Après un export ou un partage, la ligne d'annulation de Réglages est réaffichée (renderDataSafetyRows) : elle reflète la copie que l'écran d'annulation ouvrira.
  4. Suppression de la base de copies sans réponse (le plus souvent bloquée par une autre fenêtre de l'app) : le message et le statut après "Annuler" précisent que les copies pourront être effacées plus tard, quand cette fenêtre se fermera, même si l'utilisateur annule. Pas de promesse de ce genre pour une erreur franche.
  * Limite connue : une tentative dont l'échec survient à la pose de la marque ("stockage plein") laisse encore sa copie (identique à l'état). Elle est écartée de la ligne tant qu'elle est identique, mais redevient proposée dès que l'état change (nouvelle séance, export). Non traité ici, hors du périmètre demandé.
* Défauts restants (faibles) :
  * 6 : comptage des séances perdues par identifiant, limites théoriques impossibles avec des données de l'app (séance sans identifiant, identifiants en double, même séance au contenu différent).
  * 7 : "Ignorer" laisse un éventuel état mélangé (le message le dit, la copie reste dans Réglages tant que le nettoyage ne l'a pas supprimée).
  * 8 : le nettoyage des vieilles copies peut être interrompu par le rechargement, sans conséquence.
  * 9 : BACKUP_KEY_LABELS répète la liste de DB_KEYS (une nouvelle clé ne serait pas contrôlée à l'export).
  * 10 : doublons. Le nom de fichier et lastExportAt sont calculés à la fois par downloadOvrykExport et par shareOvrykBackup, CURRENT_SCHEMA_VERSION répète le 2 de migrateSchema, et summary.sessionsTotal n'est pas affiché.
  * 11 : non vérifié sous Safari, l'abandon de la création de la base IndexedDB quand on ouvre Réglages.
* Livraison 2 faite le 2026-10-14 (sw v129) : connexion par **e-mail et mot de passe** (décision de Ruben, remplace le code reçu par e-mail).
  * Réglages, section "Sauvegarde en ligne" :
    * déconnecté : formulaire e-mail (`type=email`, `autocomplete=username`) et mot de passe (`autocomplete=current-password`), bouton "Se connecter", aucun bouton d'inscription ;
    * connecté : "Connecté : adresse" (en textContent), "Vérifier la connexion", "Se déconnecter".
  * Fonctions : cloudRequest (seul point d'appel réseau, fetch, délai 15 s, `cache: no-store`, `credentials: omit`), cloudErrorMessage, readCloudSession, writeCloudSession, clearCloudSession, getFreshAccessToken (un seul renouvellement à la fois), cloudSignIn, cloudVerify, cloudSignOut, renderCloudSection. Configuration : CLOUD_URL et CLOUD_PUBLISHABLE_KEY, seules valeurs publiques présentes.
  * Appels, vérifiés dans la spécification officielle de l'API Auth (supabase/auth, openapi.yaml) :
    * connexion : `POST /auth/v1/token?grant_type=password`, corps `{email, password}` ;
    * renouvellement : `POST /auth/v1/token?grant_type=refresh_token`, corps `{refresh_token}` (jeton à usage unique) ;
    * vérification, lecture seule : `GET /auth/v1/user` ;
    * déconnexion de cet appareil seulement : `POST /auth/v1/logout?scope=local`, réponse 204 ;
    * en-têtes : `apikey: <clé publishable>` (la clé publishable va dans `apikey`, jamais dans Authorization, d'après la page "Understanding API keys"), plus `Authorization: Bearer <jeton d'accès>` pour /user et /logout ;
    * erreurs : code lu dans `error_code` (champ `code` = statut HTTP selon la spécification).
  * Aucun appel au lancement, à l'ouverture de Réglages ni par minuterie (décision 1 A : renouvellement seulement avant une action en ligne ou via "Vérifier la connexion").
  * Mot de passe jamais stocké ni journalisé, champ vidé après chaque tentative. Seule la session { access_token, refresh_token, expires_at, user { id, email }, savedAt } est gardée dans la clé exacte ovryk.cloud.auth, hors des six clés de données : absente de l'export, de la restauration et des copies.
  * Messages :
    * hors ligne : "Pas de connexion internet." ;
    * réseau injoignable, délai dépassé ;
    * 5xx ou réponse illisible : "Service de sauvegarde indisponible… projet peut-être en pause" ;
    * "E-mail ou mot de passe incorrect." seulement pour `invalid_credentials` à la connexion ;
    * 429 ou `over_request_rate_limit` : trop d'essais ;
    * toute autre réponse refusée : message neutre avec le code.
  * Renouvellement : la session n'est effacée que sur un refus définitif (`refresh_token_not_found`, `refresh_token_already_used`, `session_not_found`, `session_expired`, `user_not_found`, `user_banned`, ou `invalid_grant` sans code). Réseau coupé, délai, 5xx, réponse illisible ou autre refus : session conservée à l'identique, message honnête.
  * Déconnexion (décision 3 A) : révocation scope=local puis effacement local dans tous les cas ; hors ligne, message précisant que la session peut rester valable côté serveur.
  * "Réinitialiser l'app" (décision 2 A) efface aussi la clé exacte ovryk.cloud.auth, sans appel réseau, et le texte de confirmation le mentionne.
  * sw.js : toute requête vers un domaine `*.supabase.co`, quelle que soit la méthode, part directement au réseau, jamais en cache. Les polices Google restent mises en cache.
  * CSP : index.html n'en déclare aucune, rien à modifier.
  * Sources officielles : https://raw.githubusercontent.com/supabase/auth/master/openapi.yaml (points d'appel, corps, schéma d'erreur, scope de logout), https://supabase.com/docs/guides/auth/debugging/error-codes (codes d'erreur), https://supabase.com/docs/guides/api/api-keys (en-tête apikey pour la clé publishable).
  * Non vérifié : appel au vrai projet (aucun test avec le vrai compte), CORS depuis ovrykapp.github.io, réponse exacte d'un projet en pause, Safari et iPhone (trousseau, remplissage automatique, hors ligne réel).
* Livraison 3 codée le 2026-10-14 (sw v130) : table Supabase backups et envoi manuel d'une sauvegarde.
  * Scripts, dans dossier-lots/supabase/ :
    * backups.sql : table, RLS activé et non forcé, deux politiques SELECT et INSERT pour authenticated, droits explicites, rotation, `notify pgrst` ;
    * backups-annulation.sql : supprime la table et toutes les sauvegardes en ligne ;
    * backups-verification.sql : contrôles à lancer à la main, dont un test de rotation sans trace.
    Aucun ne contient de clé ni de mot de passe.
  * RLS est activé mais pas forcé (décision du 2026-10-14) : anon et authenticated sont soumis aux politiques, le propriétaire de la table (postgres), donc la rotation, ne l'est pas. Aucune politique UPDATE ni DELETE. Aucun droit pour anon ni public. authenticated : SELECT, et INSERT limité aux colonnes id, schema_version, sessions_count, summary, fingerprint, payload (ni user_id, rempli par auth.uid(), ni created_at).
  * Rotation (déclencheur après INSERT, fonction SECURITY DEFINER, search_path vide, droits d'exécution retirés) : pour le compte de la ligne ajoutée, garde les 30 plus récentes et la plus complète (plus grand sessions_count, à égalité la plus récente). Ne supprime jamais la ligne ajoutée ni la plus complète : il reste toujours au moins une sauvegarde.
  * **À savoir** : une sauvegarde au sessions_count absurde (par exemple modifiée à la main) serait gardée pour toujours par la rotation, comme "la plus complète". Elle se supprime alors à la main, dans le tableau de bord Supabase (Table Editor, table backups).
  * Taille : 2 Mo au plus par sauvegarde (contrainte backups_payload_size, en octets), même limite dans l'app (CLOUD_BACKUP_MAX_BYTES), mesurée en octets UTF-8. Environ 380 séances à 5 Ko ; se relève par un ALTER le jour où le message "trop volumineuse" apparaît.
  * L'empreinte (summary.checksum, hashBackupString) est toujours sur 8 caractères hexadécimaux minuscules avec zéros initiaux : conforme à la contrainte ^[0-9a-f]{8}$, vérifié sur 3 millions d'entrées dont 51 commençant par quatre zéros. Contrainte et code inchangés.
  * App :
    * bouton "Envoyer une sauvegarde maintenant" et ligne "Dernier envoi réussi" (ou "Aucun envoi depuis cet appareil"), visibles seulement une fois connecté ;
    * fonctions buildCloudBackupRow, cloudUploadBackup, cloudBackupErrorMessage, readLastUpload, utf8ByteLength, newBackupUuid ;
    * cloudRequest reçoit des en-têtes et un délai facultatifs (60 s pour l'envoi), sans changement pour les appels existants.
  * Contenu envoyé :
    * payload = le contenu exact d'un fichier d'export (même enveloppe collectAllOvrykData, même empreinte), en JSON compact, accepté tel quel par validateBackupFile ;
    * mêmes contrôles que l'export (getBackupBlocker) ;
    * jamais ovryk.cloud.auth, ovryk.cloud.lastUpload ni aucun jeton.
  * Appels :
    * envoi : `POST /rest/v1/backups`, en-têtes apikey, Authorization Bearer et `Prefer: return=minimal`, avec un identifiant uuid créé sur le téléphone ;
    * un 401 entraîne un seul renouvellement, puis un renvoi avec le même identifiant ; un doublon (23505) mène directement à la relecture ;
    * relecture légère : `GET /rest/v1/backups?id=eq.<id>&select=fingerprint,sessions_count`, sans le payload ;
    * "Sauvegarde envoyée et vérifiée" seulement si l'empreinte ET sessions_count relus correspondent.
  * Messages :
    * hors ligne (rien envoyé) ;
    * réseau ou délai (envoi non confirmé, à renvoyer) ;
    * session refusée (reconnexion) ;
    * table absente (script SQL non exécuté) ;
    * droits refusés ;
    * trop volumineuse (localement, ou 413, ou contrainte backups_payload_size) ;
    * autre règle de la table ;
    * serveur indisponible ;
    * envoi non vérifié.
  * Dernier envoi réussi mémorisé dans ovryk.cloud.lastUpload ({ at, id, fingerprint, sessionsCompleted }), hors des six clés de données : jamais exporté, jamais restauré, gardé à la déconnexion, effacé (clé exacte) par "Réinitialiser l'app" (décision 2 A).
  * Aucun appel au lancement ni à l'ouverture de Réglages, un seul envoi à la fois, aucune écriture dans les données de l'app.
  * sw.js : *.supabase.co toujours hors cache (inchangé), version v130.
  * Test du SQL sur un PostgreSQL local : **non fait**. Aucun PostgreSQL n'est disponible sur le Mac (ni installé, ni Postgres.app, ni Docker, ni paquet Node ou Python), et l'installation demanderait le réseau. Le SQL n'a été vérifié qu'à la relecture ; backups-verification.sql couvre les règles d'accès, les droits (dont l'absence d'UPDATE et de DELETE pour authenticated et de tout droit pour anon) et la rotation (section 7).
  * Mise en service :
    1. Ruben exécute backups.sql puis backups-verification.sql et transmet les résultats.
    2. Test réel sans connexion (ci-dessous).
    3. Audit puis push du code.
    4. Premier vrai envoi depuis l'iPhone.
    Si le code est en ligne avant le script, le bouton affiche "La table de sauvegarde n'existe pas encore sur Supabase" : rien n'est écrit ni marqué comme envoyé.
  * Test réel sans connexion, à lancer seulement quand Ruben le décide. Il lit l'adresse et la clé publique depuis index.html, sans les retaper, et n'utilise aucun jeton ni mot de passe :
    ```
    cd "/Users/rubenzerbib/Desktop/Ovryk app"
    URL=$(sed -n "s/.*var CLOUD_URL = '\([^']*\)'.*/\1/p" index.html)
    KEY=$(sed -n "s/.*var CLOUD_PUBLISHABLE_KEY = '\([^']*\)'.*/\1/p" index.html)
    curl -s -i "$URL/rest/v1/backups?select=id&limit=1" -H "apikey: $KEY"
    curl -s -i -X POST "$URL/rest/v1/backups" -H "apikey: $KEY" -H "Content-Type: application/json" -H "Prefer: return=minimal" -d '{"sessions_count":0,"summary":{},"fingerprint":"00000000","payload":"{}"}'
    ```
    * Réponse correcte, c'est-à-dire un refus, pour les deux : 401 avec `"code":"42501"` (permission denied for table backups), ou 404 avec `"code":"PGRST205"` pour la première.
    * Échec de sécurité, à signaler : 200 (même avec `[]`) pour la première, 201 pour la seconde.
* Livraison 4 codée le 2026-10-14 (sw v131 puis v132) : restauration depuis la sauvegarde en ligne. Plan approuvé le 2026-10-14 avec les décisions de Ruben.
  * Numérotation : cette livraison 4 reprend la restauration prévue au point 5 de la section 10. La sauvegarde automatique après une séance (point 4 de la section 10) et la suppression des sauvegardes en ligne restent pour la livraison 5.
  * Écart avec la section 10 : pas d'instantané "avant restauration" envoyé en ligne. Ruben a demandé une lecture seule côté serveur ; la copie IndexedDB de l'état actuel, prise avant tout remplacement, protège seule.
  * Commit A (sw v131) : déplacement pur. Le code qui suit la lecture d'un fichier importé passe dans openRestoreFromParsed(parsed, nomSource), sans changement de comportement. Suites de la livraison 1 relancées, au vert.
  * Commit B (sw v132) : restauration en ligne.
    * Bouton "Restaurer depuis une sauvegarde en ligne", visible une fois connecté. Aucun appel au lancement ni à l'ouverture de Réglages.
    * Liste au clic : `GET /rest/v1/backups?select=id,created_at,sessions_count,fingerprint,last_session:summary->>lastSessionAt&order=created_at.desc&limit=40`, sans payload. La clé lastSessionAt existe dans summary (summarizeOvrykData), donc dans toute ligne envoyée par l'app ; si elle est absente ou vide, la date de dernière séance n'est pas affichée.
    * Chaque ligne : date d'envoi (created_at), séances terminées, date de la dernière séance, empreinte. Repères : "La plus complète" (même règle que la rotation), "Envoyée depuis cet appareil" (id de ovryk.cloud.lastUpload), "Identique à ce téléphone" (empreinte des données actuelles, calculée sans rien écrire). Les lignes mal formées sont ignorées. Tout est affiché en textContent.
    * Choix d'une ligne : téléchargement du seul payload (`GET /rest/v1/backups?id=eq.<id>&select=payload,fingerprint,sessions_count`, délai 60 s).
    * Contrôles avant tout, dans l'ordre :
      1. une ligne exactement (aucune : "n'existe plus en ligne") ;
      2. empreinte et nombre de séances égaux à ceux de la ligne choisie ;
      3. payload JSON lisible ;
      4. summary.checksum présent et égal à l'empreinte de la ligne ;
      5. nombre de séances terminées recalculé sur les données égal à sessions_count (décision : refus sinon) ;
      6. puis openRestoreFromParsed, exactement le chemin d'un fichier importé : validateBackupFile (qui recalcule l'empreinte sur les données), écran de comparaison, deuxième confirmation, copie IndexedDB, marque, annulation.
    * getBackupBlocker n'est pas utilisé (décision) : il bloquerait la restauration sur un téléphone vide. Messages de validateBackupFile inchangés ("fichier"), précédés de "Restauration refusée :". Date de l'écran de comparaison : date d'export contenue dans la sauvegarde.
    * Session : renouvellement si besoin, un seul rejeu après un 401. Session révoquée : effacée, liste retirée. À la déconnexion, la liste est vidée : celle d'un compte n'est jamais montrée pour un autre.
    * Aucune écriture locale avant la deuxième confirmation, aucune écriture côté serveur, aucun changement SQL ni droit ajouté.
  * Tests automatiques : test_restore_cloud.py, 47 sur 47, avec Supabase simulé et des données fabriquées dans le test (aucun vrai export, aucune vraie clé de session).
* Livraison 5 codée le 2026-10-14 (sw v133 puis v134) : envoi automatique de la sauvegarde en ligne après chaque séance. Plan approuvé le 2026-10-14 avec les arbitrages de Ruben.
  * Commit A (sw v133) : découpage pur. Le cœur de l'envoi passe dans runCloudUpload(row, finish), partagé par le bouton et l'envoi automatique, sans changement de comportement. Suites de la livraison 3 et 4 relancées, au vert.
  * Commit B (sw v134) : envoi automatique et affichage.
    * Option "Envoi automatique après chaque séance" dans Réglages (visible une fois connecté), désactivée par défaut, dans ovryk.cloud.prefs, écrite au seul appui.
    * Déclenchement : à la fin de finishActiveSession, après l'enregistrement de la séance, l'export fichier (inchangé, question 8), l'avancée des cycles et l'affichage de l'écran de départ, dans un setTimeout avec try : rien de la fin de séance n'attend l'envoi ni n'en dépend. Même cœur et même verrou que le bouton.
    * Pas d'envoi automatique (essai noté "non envoyé") si : verrou pris, envoi automatique il y a moins de 2 minutes, garde-fou (séances terminées du téléphone inférieures à celles du dernier envoi vérifié du même compte ; un lastUpload sans userId compte par prudence), ou état vide ou illisible (getBackupBlocker). L'envoi manuel reste possible et lève le garde-fou.
    * ovryk.cloud.lastAttempt : dernier essai, automatique ou manuel (en cours, réussi, échec, non confirmé, non envoyé), avec le texte du message seulement. "En cours" est écrit avant l'envoi : une appli tuée en plein envoi s'affiche "interrompu, non confirmé".
    * ovryk.cloud.lastUpload reçoit le champ optionnel userId (compte dont le jeton a servi).
    * Réglages, lecture seule : dernier envoi réussi, dernier essai, "À renvoyer : N séances terminées pas encore en ligne" (par nombre de séances) ou le message du garde-fou, rappel si le dernier envoi réussi a plus de 7 jours et qu'il reste des séances à renvoyer (connecté ou non ; rien si aucun envoi n'a jamais réussi).
    * Accueil : une seule ligne discrète sous les bandeaux, visible seulement en cas de problème (dernier essai échoué, non confirmé ou interrompu, garde-fou actif, ou plus de 7 jours avec des séances à renvoyer). Un appui ouvre Réglages.
    * Réinitialiser l'app efface aussi ovryk.cloud.prefs et ovryk.cloud.lastAttempt. Toutes les clés ovryk.cloud.* restent hors DB_KEYS : jamais exportées, restaurées ni copiées.
    * Aucun appel ni écriture au lancement, aucun changement SQL ni droit ajouté, rotation à 30 inchangée.
    * Écart voulu avec la section 10 : pas de nouvel essai au retour du réseau (événement "online"), pas de message après la séance. Le prochain envoi, automatique ou manuel, rattrape.
  * Tests automatiques : dossier-lots/tests/test_auto_upload.py, Supabase simulé, données fabriquées.

## Lot de nettoyage : points non bloquants de l'audit de la livraison 4 (2026-10-14)

Audit de c0b9104 et 9f186ff : verdict SÛR, aucun point bloquant. À traiter dans un lot de nettoyage, pas avant (aucun n'écrit de données sans les deux confirmations).

1. Une réponse en ligne qui arrive après une déconnexion ou un changement de compte faits dans une autre fenêtre ouvre quand même l'écran de restauration (cloudDownloadBackup ne compare pas la session de départ à la session actuelle).
2. Une réponse tardive remplace un écran de restauration déjà ouvert (par exemple un fichier importé entre temps) : l'écran affiche la sauvegarde en ligne, mais confirmRestore a déjà retenu l'ancien contenu et appliquerait celui-là. Pendant la copie de sécurité, renderRestorePage peut aussi débloquer les boutons.
3. L'écran de restauration s'ouvre par-dessus n'importe quelle vue si l'utilisateur a quitté Réglages pendant le téléchargement, y compris pendant une séance en cours.
4. Le recalcul du nombre de séances est contournable avec un ancien format (listes à la racine, sans data.sessions) : ce contrôle n'est fait que si data.sessions est une liste. Cas théorique, l'empreinte FNV 32 bits détecte l'abîmé, pas la falsification.
5. Le délai de la liste des sauvegardes est de 15 s (délai par défaut) au lieu de 60 s comme le téléchargement.
6. Le renouvellement de session pendant le téléchargement peut écrire ou effacer ovryk.cloud.auth avant toute confirmation (voulu depuis la livraison 2, à documenter ou à isoler).
7. Des dates affichées ne sont pas couvertes par l'empreinte : "dernière le" de la liste (colonne summary) et "exportée le" de l'écran de comparaison (exportedAt).
8. Le repère "Identique à ce téléphone" est absent juste après une restauration : les migrations et le rattrapage du catalogue au rechargement changent l'empreinte locale.
9. Messages approximatifs : une ligne d'un autre compte donne "n'existe plus (remplacée par un envoi plus récent)", les refus de validateBackupFile parlent de "fichier", et "Dernier envoi réussi" n'est pas propre à chaque compte.

### Points non corrigés de l'audit de la livraison 5 (2026-10-14)

Audit de 992a6b7 et 326306f : verdict SÛR, aucun point bloquant. Les points 1 à 3 de l'audit (un "non envoyé" qui efface l'alerte d'un échec, "À renvoyer" à 0 sans envoi de référence, dernier essai invisible une fois déconnecté) sont corrigés dans le commit C (sw v135). Restent, pour le lot de nettoyage :

1. Réinitialiser l'app pendant un envoi en cours : la requête est coupée au rechargement, son retour d'erreur recrée ovryk.cloud.lastAttempt (non confirmé, userId null) et l'Accueil d'une appli vierge affiche "dernier envoi non confirmé". Réinitialiser ne tient pas compte du verrou cloudBusy.
2. Rechargement en plein envoi : l'état enregistré est honnête (non confirmé) mais le texte gardé parle de service injoignable, alors que c'est l'appli qui a été rechargée. Le cas "interrompu" n'apparaît que si le JavaScript ne tourne plus du tout.
3. Verrou bloqué si une exception survient dans un callback réseau : le try de startCloudAttempt n'attrape que les erreurs synchrones, le catch de cloudRequest avale les autres (done vaut déjà true). cloudBusy reste vrai et l'essai reste "en cours" jusqu'au rechargement. Déjà vrai pour le bouton manuel, étendu à l'envoi automatique.
4. Calcul lourd juste après la fin de séance : buildCloudBackupRow (sérialisation, empreinte, mesure en octets, jusqu'à 2 Mo) et plusieurs relectures des séances dans le setTimeout. Un court gel est possible sur un long historique. Non mesuré.
5. Fenêtre de rotation plus courte : avec un envoi par séance, les 30 sauvegardes les plus récentes couvrent environ 30 séances (la plus complète reste toujours gardée).
6. Écriture de liftBaseMode au deuxième démarrage d'une installation neuve (préexistante, commit 7b9a195, sans lien avec la livraison 5) : la clé ovryk.exercises change au deuxième lancement puis se stabilise.

Test automatique de la livraison 5 : dossier-lots/tests/test_auto_upload.py (51 sur 51, Supabase simulé, données fabriquées).

Test automatique de la livraison 4 : dossier-lots/tests/test_restore_cloud.py (47 sur 47, Supabase simulé, données fabriquées). Il prend en argument un dossier de travail et attend le site servi sur http://127.0.0.1:8765.
