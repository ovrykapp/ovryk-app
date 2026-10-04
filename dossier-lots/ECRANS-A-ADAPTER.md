# Écrans de la maquette à adapter avant de les construire

La maquette a été dessinée en deux temps. Au départ, chaque cycle appartenait à un mouvement. Ensuite, tu as précisé que les 12 cycles sont génériques et que le tirage choisit le cycle, pas le mouvement. Plusieurs écrans montrent encore l'ancien modèle. Ils sont à construire selon les adaptations ci-dessous, pas à l'identique.

## Écrans concernés

### 24. Tirer mes cycles (lot 07)
* Maquette : l'utilisateur choisit un nombre de cycles et des mouvements possibles par famille, l'app tire des mouvements.
* À faire : l'utilisateur choisit les mouvements à activer (exercices de catégorie Lifting) et leur 1RM. L'app tire un cycle pour chacun. Supprimer les familles de mouvements. Le réglage "séances par semaine" de la maquette devient la règle R12 : la deuxième séance d'un mouvement dans la semaine est plus légère, sans réglage à l'activation.

### 29. Cycles tirés au sort (lot 07)
* Maquette : chaque carte est un mouvement avec sa famille et son cycle propre.
* À faire : chaque carte est un mouvement choisi, avec le cycle tiré ("Cycle 7 : Volume vers vagues et test"), sa durée, la semaine 1 calculée avec le 1RM, et un bouton pour relancer ce tirage.

### 25. Détail d'un cycle (lot 07)
* Maquette : le détail du cycle Snatch.
* À faire : le détail du cycle générique appliqué au mouvement, avec les charges en kg calculées sur son 1RM. Une page existe déjà : cycle-detail-page (openCycleDetailPage). La restyler.

### 22. Configurer l'exercice (lot 07)
* Maquette : réglage des semaines du Snatch avec "Hausse".
* À faire : afficher le cycle de l'exercice et permettre de modifier le pourcentage d'une semaine. Retirer toute notion de hausse constante.

### 27. Fin de cycle (lot 06)
* Maquette : le prochain cycle tiré dans la famille libérée, avec un mouvement différent.
* À faire : le prochain cycle est un cycle générique tiré pour le même mouvement, jamais le même que celui qui finit. Retirer les familles.

### 30. Coordination des cycles (lot 08)
* Maquette : lignes par mouvement (Snatch, Push Press, Squat Clean, Back Squat) avec des phases propres à chaque mouvement.
* À faire : une ligne par mouvement actif. Les phases viennent du cycle générique du mouvement. Les départs décalés se calculent avec R7.

### 28. Charge de la semaine (lot 13)
* Maquette : l'exemple parle du Power Clean et du soulevé de terre roumain. Ce sont des données d'exemple.
* À faire : les exercices et les zones viennent des vraies données.

## Écrans à ne pas construire tels quels

### 20, 21, 22 (créer un programme de zéro, éditer une séance)
* Le parcours "Créer de zéro" de la maquette correspond à l'éditeur de routine existant. Ne pas recréer des écrans en parallèle : restyler l'éditeur de routine (lot 09).

### 8. Vérifier l'import
* L'import d'un programme par photo, PDF ou texte est abandonné (décision 8). Cet écran sert de modèle de validation pour l'import CSV du lot 15.

### 18. Compte et sauvegarde
* Sans connexion Apple. Boutons Google et lien par e-mail seulement (lot 16).

## Écrans informatifs
* 2, 3, 10, 11, 13 : données d'exemple. Les valeurs (charges, pourcentages, noms) viennent des vraies données.
