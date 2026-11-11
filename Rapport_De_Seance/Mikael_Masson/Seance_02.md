# Rapport de séance 2 : 11 novembre 2026

**Projet :** BASTARD (drone intercepteur anti-UAS)
**Sujet :** mesure des composants reçus, début de la modélisation 3D et essais de soudure
**Auteur :** Mikael Masson

---

## 1. Objectif de la séance

1. Mesurer les composants déjà reçus, pour disposer de cotes réelles plutôt que des seules cotes des fiches fabricant.
2. Commencer la modélisation 3D de ces composants dans Fusion 360, en vue de la conception de la monocoque.
3. Récupérer les modèles 3D open source des cartes électroniques.
4. S'entraîner à la soudure avant de souder les moteurs sur l'ESC 4-en-1.

## 2. Matériel et logiciels

| Élément | Détail |
|---|---|
| Mesure | Pied à coulisse numérique |
| CAO | Autodesk Fusion 360 (fichiers `.f3d`) |
| Scripts | API Python de Fusion 360 (Utilities > Scripts and Add-Ins) |
| Composants mesurés | GPS Holybro Micro M10, UBEC Hobbywing 5A V2 Air, moteur Axisflying AI2807 1300 KV, hélice HQProp 7×5.5 |
| Soudure | Fer à souder, chutes de fil pour les essais |

## 3. Déroulé

### 3.1 Mesure des composants

Toutes les cotes sont relevées au pied à coulisse numérique. La dernière colonne rappelle la valeur de la fiche fabricant quand elle existe.

**GPS Holybro Micro M10 (avec boîtier)**

| Cote | Mesure | Fabricant |
|---|---|---|
| Longueur (sens de la flèche) | 34,45 mm | 34 mm |
| Largeur | 27,93 mm | 28 mm |
| Épaisseur | 10,79 mm | 11 mm |

**Régulateur Hobbywing UBEC 5A V2 Air (sans les fils)**

| Cote | Mesure | Fabricant |
|---|---|---|
| Longueur hors tout | 62,23 mm | 50 mm |
| Largeur | 17,39 mm | 17 mm |
| Épaisseur | 7,97 mm | 10 mm |

- Remarque : la longueur mesurée dépasse celle de la fiche de 12 mm. Elle inclut le condensateur qui dépasse en bout de carte.
- Remarque : l'épaisseur est mesurée sur le corps. Celle du condensateur reste à mesurer, c'est peut-être elle qui explique les 10 mm de la fiche.

**Moteur Axisflying AI2807 1300 KV**

| Cote | Mesure | Fabricant |
|---|---|---|
| Diamètre extérieur de la cloche | 33,62 mm | 33,6 mm |
| Hauteur embase + cloche | 20,52 mm | — |
| Hauteur totale, arbre compris | 35,68 mm | 35,7 mm |
| Bout à bout de deux pattes de fixation opposées | 25,05 mm | — |
| Moyeu central de l'embase | 14,44 mm | — |

- L'arbre dépasse donc de 15,16 mm au-dessus de la cloche (35,68 − 20,52). Cette cote fixe le plan des hélices.
- Avec les trous M3 sur un cercle de Ø19 mm (donnée fabricant), les pattes font environ 6 mm de large (25,05 − 19).

**Hélice HQProp 7×5.5**

| Cote | Mesure | Fabricant |
|---|---|---|
| Diamètre du moyeu | 13,99 mm | 14 mm |

**→ Les mesures confirment les cotes fabricant à quelques dixièmes de millimètre près, sauf pour l'UBEC dont l'encombrement réel est plus long que la fiche.**

### 3.2 Modélisation 3D dans Fusion 360

Chaque composant est modélisé dans Fusion 360 et enregistré en `.f3d`. Les modèles sont **paramétriques** : les cotes sont des paramètres utilisateur (Modify > Change Parameters) liés aux esquisses, ce qui permet de corriger une mesure sans redessiner la pièce. Ils sont générés par des scripts Python (API Fusion 360), un par composant.

| Composant | Contenu du modèle | Paramètres |
|---|---|---|
| GPS Holybro Micro M10 | Boîtier aux cotes mesurées, coins arrondis, flèche gravée pour le sens de montage | `GPS_longueur`, `GPS_largeur`, `GPS_hauteur`… |
| UBEC Hobbywing 5A | Enveloppe aux cotes hors tout mesurées, sans les fils | `UBEC_longueur`, `UBEC_largeur`, `UBEC_hauteur`… |
| Moteur Axisflying AI2807 | Modèle détaillé : embase à 4 pattes et trous M3, stator 12 dents, bobinages, 14 aimants, cloche à 8 rayons, arbre M5 | 26 paramètres `MOT_…` |

Repère commun à tous les modèles : origine au centre de la face inférieure, Z vers le haut. Pour le moteur, Z est l'axe de rotation et Z = 0 la face d'appui de l'embase.

Chaque paramètre indique son origine dans son commentaire :

- **MESURE** : relevé au pied à coulisse (tableaux du § 3.1).
- **FABRICANT** : donnée de la fiche (trous M3 sur Ø19, arbre M5, stator Ø28 × 7 pour le moteur).
- **ESTIME** : valeur estimée d'après les photos (rayons des coins, épaisseur de l'embase du moteur, parois, aimants). Ces valeurs ne changent pas l'encombrement extérieur.

Les fils ne sont modélisés sur aucun composant.

### 3.3 Récupération des modèles open source

| Carte | Modèle récupéré | Remarque |
|---|---|---|
| D-Robotics RDK X5 | Modèle 3D open source de la carte | Remplace l'enveloppe 85 × 56 × 20 mm utilisée jusqu'ici |
| Matek H743-SLIM | Modèle open source de la **H743-SLIM V3** | Mêmes dimensions que la V4 du projet : utilisé tel quel |

Ces deux cartes n'ont donc pas besoin d'être mesurées ni redessinées.

### 3.4 Essais de soudure

Quelques soudures d'essai ont été réalisées pour prendre en main le fer. L'objectif est de préparer la prochaine étape : **souder les fils des quatre moteurs sur l'ESC 4-en-1**.

## 4. Problèmes rencontrés et solutions

| Problème | Cause | Solution |
|---|---|---|
| Un fichier `.step` importé n'a ni esquisse ni paramètre | Le format STEP ne contient que la géométrie finale | Générer les pièces par script Python dans Fusion 360, avec esquisses cotées et paramètres utilisateur |
| Fusion 360 : *« Failed to create script. Input targetFolder is not a directory »* | Le champ Folder Location désignait un dossier qui n'existait pas | Indiquer un dossier existant : Fusion crée lui-même le sous-dossier au nom du script |
| Script : *« Part Design documents can only contain one component »* | Le script créait un nouveau composant dans un document de type Part Design | Script corrigé : il dessine dans le composant principal quand le document n'accepte qu'un composant |
| Fenêtre de sélection : impossible de choisir le fichier `.py` | « Script or add-in from device » attend un dossier, pas un fichier | Sélectionner le dossier qui porte le même nom que le script |

## 5. Bilan

| Tâche | Résultat |
|---|---|
| Mesure du GPS Holybro Micro M10 | ✅ |
| Mesure de l'UBEC Hobbywing 5A | ✅ (épaisseur du condensateur à mesurer) |
| Mesure du moteur AI2807 | ✅ |
| Mesure du moyeu de l'hélice HQProp 7×5.5 | ✅ |
| Modèle 3D du GPS (`.f3d`) | ✅ |
| Modèle 3D de l'UBEC (`.f3d`) | ✅ |
| Modèle 3D du moteur (`.f3d`) | ✅ (détails internes estimés) |
| Modèle 3D de l'hélice | ⏳ À faire |
| Modèles open source RDK X5 et Matek H743-SLIM | ✅ Récupérés |
| Essais de soudure | ✅ |
| Soudure des moteurs sur l'ESC 4-en-1 | ⏳ Prochaine séance |

**Conclusion :** les composants déjà reçus sont mesurés et trois d'entre eux sont modélisés en 3D. Avec les modèles open source du RDK X5 et du Matek, la bibliothèque de pièces nécessaire à la conception de la monocoque est bien avancée.

## 6. Reste à faire

- [ ] Modéliser l'hélice HQProp 7×5.5 (moyeu Ø13,99 mm, disque balayé de 7 pouces)
- [ ] Mesurer l'épaisseur du condensateur de l'UBEC et corriger `UBEC_hauteur` si besoin
- [ ] Vérifier sur le moteur les cotes estimées (épaisseur de l'embase, jeu sous la cloche)
- [ ] Mesurer et modéliser les composants restants à réception : batterie, ESC 4-en-1, récepteur, caméra, connecteur XT60, châssis
- [ ] Réunir toutes les pièces dans un assemblage Fusion 360 et commencer la conception de la monocoque
- [ ] Souder les moteurs sur l'ESC 4-en-1
- [ ] Reste de la séance 1 : tester l'OSD du Matek, nettoyer le résidu de flux près de l'USB-C

## Références

- Rapport de la séance 1 (réception et contrôle du Matek H743-SLIM-V4) : `2026-11-06_rapport_seance_FC_Matek_H743.md`
- Modèle 3D du RDK X5 (D-Robotics) : https://archive.d-robotics.cc/downloads/hardware/rdk_x5/RDK_X5_LPDDR4_4266MHz_V1P0_pcb.stp
- Page produit Matek H743-SLIM : https://www.mateksys.com/?p=12864
- Fichiers CAO Holybro Micro M10 : https://docs.holybro.com/gps-and-rtk-system/m8n-m9n-m10-gps/micro-m10-m9n-gps/download
