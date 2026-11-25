# Rapport de séance : 25 novembre 2026

**Projet :** BASTARD (drone intercepteur anti-UAS)
**Sujet :** alimentation de la radiocommande et choix de l'ESC v1 du projet
**Auteur :** Mikael Masson

---

## 1. Objectifs de la séance

1. Équiper la radiocommande **RadioMaster Pocket** de ses batteries.
2. Remettre en état l'ESC utilisé au banc d'essai du 17 novembre pour qu'il devienne l'**ESC v1** du projet.

## 2. Matériel

| Élément | Détail |
|---|---|
| Radiocommande | RadioMaster Pocket, ELRS 2,4 GHz, LBT, Mode 2, firmware EdgeTX |
| Batteries de la radio | 2 × accus Li-ion 18650 (3,7 V nominal chacun) |
| ESC v1 retenu | HAKRC 8B50A 4-en-1, BLHeli_S, 2–6S, 50 A continus / 60 A en pointe |
| ESC reçu le 24 novembre | Carte marquée HK8B20I V1.2 (ESC commandé), gardé en réserve |
| Outillage | Fer à souder, flux, tresse ou pompe à dessouder |

## 3. Déroulé

### 3.1 Batteries de la radiocommande

La Pocket est livrée sans batterie. Elle fonctionne avec **2 accus 18650 Li-ion de 3,7 V**, montés en série. Sa plage de fonctionnement est de **6,6 à 8,4 V**, et elle se recharge directement par son port **USB-C** (charge rapide QC3).

**Fait :** mise en place des **2 accus 18650** dans le logement de la radio.

| Caractéristique | Valeur |
|---|---|
| Accus | 2 × 18650 Li-ion, 3,7 V |
| Tension de fonctionnement | 6,6–8,4 V |
| Charge | USB-C intégré, QC3 |

### 3.2 Choix de l'ESC v1 et nettoyage

Deux ESC 4-en-1 sont maintenant disponibles :

| | HAKRC 8B50A (banc d'essai) | HK8B20I V1.2 (reçu le 24 novembre) |
|---|---|---|
| Firmware | BLHeli_S 8 bits | 8 bits (« 8B ») |
| Courant | 50 A continus / 60 A en pointe | À confirmer sur la fiche |
| Fixation | 30,5 × 30,5 mm | À mesurer (environ 20 × 20 mm à l'œil) |
| Pastilles batterie | − à gauche, + à droite | **+ à gauche, − à droite** |
| Connecteur 8 broches | − + 1 2 3 4 N C | Même ordre sur la sérigraphie (à confirmer au multimètre) |
| État | Puissance, condensateur et XT60H-M déjà soudés | Neuf |

**Décision : le HAKRC 8B50A devient l'ESC v1 du projet.**

Raisons :
- il se fixe **directement sous le Matek H743-SLIM-V4**, qui n'accepte que l'entraxe 30,5 mm ;
- les fils de puissance 12 AWG, le condensateur 1000 µF 35 V et la borne XT60H-M sont **déjà en place** ;
- son brochage a déjà été relevé et la nappe préparée pendant la séance du 17 novembre ;
- sa marge en courant reste suffisante pour les Axisflying AI2807, qui tirent moins de 40 A en pointe.

Le HK8B20I est gardé en réserve, comme candidat pour une version plus compacte.

**Nettoyage fait :** **dessoudage des 3 fils du moteur 2807 de test** sur la voie M1. Les pastilles M1 sont libérées pour les moteurs définitifs.

## 4. Points de vigilance

- **Changement d'ESC plus tard :** sur le HK8B20I, les pastilles batterie sont **inversées** par rapport au HAKRC. Il ne faudra pas souder de mémoire.
- **Pastilles M1 :** après le dessoudage, vérifier à la loupe qu'aucun reste d'étain ne fait de pont entre deux pastilles voisines.
- **Accus 18650 :** respecter le sens indiqué dans le logement. Une inversion peut endommager la radio.

## 5. Bilan

| Point | Résultat |
|---|---|
| Accus 18650 installés dans la Pocket | ✅ |
| Choix de l'ESC v1 (HAKRC 8B50A) | ✅ |
| Moteur de test dessoudé de la voie M1 | ✅ |
| HK8B20I : entraxe et brochage relevés | ⏳ À faire |

**Conclusion :** la radiocommande est équipée de ses batteries, et le projet a maintenant un ESC de référence. Le HAKRC 8B50A est déjà câblé côté puissance et se fixe directement avec le Matek. Les pastilles moteur sont libres pour les AI2807.

## 6. Reste à faire

- [ ] Première charge de la Pocket en USB-C, puis lecture de la tension à l'écran
- [ ] Régler l'alarme de batterie basse dans EdgeTX
- [ ] Appairer la Pocket avec le récepteur RadioMaster RP3 V2 (ELRS)
- [ ] Contrôler les pastilles M1 à la loupe après le dessoudage
- [ ] Reprendre les points ouverts de la séance du 17 novembre s'ils ne sont pas faits : soudures de puissance, pattes du condensateur, nappe recâblée et contrôlée au multimètre
- [ ] Souder les 4 moteurs AI2807 à leur réception
- [ ] Mesurer l'entraxe et la taille du HK8B20I
- [ ] Mettre à jour `Cotes_composants_STEP.md` : ESC v1 = HAKRC 8B50A, 38,5 × 41 mm, 12,5 g, entraxe 30,5 mm

## Références

- RadioMaster, Pocket Radio Controller (M2) : https://radiomasterrc.com/products/pocket-radio-controller-m2
- Fiche technique de la Pocket (tension de fonctionnement, batteries) : https://hobbyking.com/radiomaster-pocket-elrs-16-channel-hall-gimbals-2-4ghz-transmitter-transparent-gray-1.html
- Notice HAKRC 8BIT/32BIT 4-in-1 ESC : https://manuals.plus/ae/1005005956508797
- Rapport de séance du 17 novembre 2026 : `2026-11-17_rapport_seance_3_banc_ESC_HAKRC.md`
