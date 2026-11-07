# Rapport de séance : 6 novembre 2026

**Projet :** BASTARD (drone intercepteur anti-UAS)
**Sujet :** réception et contrôle du contrôleur de vol Matek H743-SLIM-V4
**Auteur :** Mikael Masson

---

## 1. Objectif de la séance

1. Vérifier que le contrôleur de vol **Matek H743-SLIM-V4** reçu est authentique et fonctionne. Matek signale lui-même que des contrefaçons de ce modèle circulent, avec des problèmes d'OSD sur des cartes achetées chez certains revendeurs.
2. Remplacer le firmware d'usine par **ArduPilot (ArduCopter)** et vérifier les capteurs.

## 2. Matériel et logiciels

| Élément | Détail |
|---|---|
| Contrôleur de vol | Matek H743-SLIM-V4 (STM32H743VIH6, 2 × ICM42688P, DPS368, OSD AT7456E, 7 UART, 1 CAN, 13 PWM) |
| Multimètre | Metrix MX 5006 |
| Poste | MacBook Pro (macOS, Apple Silicon) |
| Flash | STM32CubeProgrammer v2.23.0 (ST) |
| Station sol | QGroundControl v5.1 Stable (Mission Planner ne fonctionne que sous Windows) |
| Firmware | ArduCopter V4.7.2 (fb773567), cible `MatekH743`, fichier `arducopter_with_bl.hex` (firmware.ardupilot.org) |

## 3. Déroulé

### 3.1 Contrôle visuel

**Emballage.** Sachet antistatique Matek avec étiquette produit et QR code. Cela ne prouve rien, car les contrefacteurs copient aussi les emballages.

**Face inférieure.** La sérigraphie est nette et conforme : logo Matek, « H743-SLIM V4 », pastilles Vbat, 4V5, 5V, G, Vsw, VTx, C1/C2, CAN, etc.
- Remarque : il y a une zone de **résidu de flux** sous les pattes du port USB-C. C'est probablement lié à la soudure manuelle de ces pattes en usine, ce qui est courant, mais c'est à nettoyer à l'alcool isopropylique.

**Face supérieure.** Composants identifiés, tous conformes à la fiche Matek :

| Fonction | Composant | Marquage relevé |
|---|---|---|
| Microcontrôleur | STM32H743VIH6 | Logo ST, « STM32H7… 3VIH6 », logo e2, datamatrix |
| IMU (× 2) | ICM42688P | « I428P » sur les deux puces |
| Baromètre | DPS368 | Boîtier métallique avec évent |
| OSD | AT7456E | « AT7456E » |
| Alimentations | 2 BEC | Inductances « 100 » (10 µH) |

Le placement et les soudures sont propres et réguliers.

### 3.2 Test de court-circuit (hors tension)

Le multimètre était en mode Ω / continuité, sonde noire sur G, carte débranchée de tout.

| Mesure | Résultat |
|---|---|
| G ↔ G (contrôle des sondes) | Continuité (normal) |
| Vbat ↔ G | Pas de court-circuit |
| 4V5 ↔ G | Pas de court-circuit |
| 5V ↔ G | Pas de court-circuit |
| Vbat ↔ 5V | Pas de court-circuit |

**→ Aucun court-circuit détecté.**

### 3.3 Premier branchement USB

Précautions prises : carte seule, alimentée uniquement par l'USB, sans aucun périphérique.

- Au branchement normal, macOS détecte **« INAV STM32 Virtual ComPort in FS Mode »**. Matek livre donc la carte avec un firmware INAV d'usine. Elle se présente comme un port série USB, et pas comme un clavier ou un autre périphérique HID : pas de risque d'injection de commandes.
- En **mode DFU** (bouton BOOT enfoncé au branchement), macOS détecte **« STMicroelectronics DFU in FS Mode »**.

```
system_profiler SPUSBHostDataType
  DFU in FS Mode:
    Manufacturer: STMicroelectronics
    Serial Number: 200364500000
    Link Speed: 12 Mb/s
```

### 3.4 Identification du microcontrôleur (STM32CubeProgrammer)

Connexion en USB DFU (VID `0x0483`, PID `0xDF11`) :

| Champ | Valeur lue | Valeur attendue |
|---|---|---|
| Device | STM32H7xx | STM32H7 ✅ |
| Device ID | **0x450** | 0x450 (STM32H742/743/750/753) ✅ |
| Taille flash | **2 MB** | 2 MB (H743VIH6) ✅ |
| CPU | Cortex-M7 | Cortex-M7 ✅ |

**→ Le microcontrôleur se comporte comme une vraie STM32H743.**

### 3.5 Effacement et flash d'ArduPilot

1. **Effacement complet de la flash** (mass erase), qui supprime INAV : *« Mass erase command correctly executed »* (16:46:49).
2. **Flash** de `arducopter_with_bl.hex` à l'adresse `0x08000000`.
3. **Redémarrage sans BOOT** : la carte démarre sous ArduCopter et QGroundControl s'y connecte.

### 3.6 Vérification des capteurs (QGroundControl)

Journal de démarrage :

```
[16:52:45.669] Info: Initialising ArduPilot
[16:52:46.434] Info: Barometer 1 calibration complete
[16:52:46.515] Info: ArduCopter V4.7.2 (fb773567)
[16:52:46.515] Info: ChibiOS: d103983f
[16:52:46.515] Info: MatekH743 004C0020 34345105 30323534
[16:52:46.515] Info: RCOut: Initialising
[16:52:46.515] Info: IMU0: fast sampling 2.0kHz/2.0kHz
[16:52:46.515] Info: IMU1: normal sampling 1.0kHz/1.0kHz
[16:52:46.515] Info: Frame: UNSUPPORTED
[16:52:47.780] Info: ArduPilot Ready
[16:52:47.780] Info: AHRS: DCM active
[16:52:47.783] Info: RCOut: PWM:1-13
[16:52:49.782] Info: EKF3 IMU0 initialised
[16:52:49.782] Info: EKF3 IMU1 initialised
[16:52:49.783] Info: AHRS: EKF3 active
[16:52:51.128] Info: EKF3 IMU1 tilt alignment complete
[16:52:51.131] Info: EKF3 IMU0 tilt alignment complete
[16:53:10.770] Critical: PreArm: Motors: Check frame class and type
```

Le numéro unique de la carte (`004C0020 34345105 30323534`) est noté pour la traçabilité.

État des capteurs (Sensor Status) :

| Capteur | État | Interprétation |
|---|---|---|
| Gyro | Normal | ✅ |
| Accelerometer | Normal | ✅ |
| Absolute pressure | Normal | ✅ Baromètre OK (altitude lue : 0,3 m) |
| Magnetometer | Error | Normal : la carte n'a pas de boussole intégrée, il faut un module GPS avec boussole |
| AHRS | Error | Normal : ni boussole ni GPS branchés |
| Pre-Arm Check | Error | Normal : `FRAME_CLASS` et `FRAME_TYPE` ne sont pas réglés |
| Logging | Disabled | Pas de carte microSD insérée |

### 3.7 Paramètres OSD

`OSD_TYPE = MAX7456` (compatible AT7456E) et `OSD1_ENABLE = Enabled` sont déjà réglés par défaut sur la cible MatekH743 : aucune modification n'est nécessaire.

## 4. Problèmes rencontrés et solutions

| Problème | Cause | Solution |
|---|---|---|
| STM32CubeProgrammer : *« No debug probe detected »* | Interface réglée sur ST-LINK par défaut | Sélectionner **USB** dans la liste en haut à droite |
| STM32CubeProgrammer : *« No DFU detected »* | Carte pas (ou plus) en mode DFU au moment de l'actualisation | Rebrancher avec BOOT enfoncé, autoriser l'accessoire dans macOS, actualiser le port (USB1) puis Connect |
| Message *« Please disconnect device n:1 and connect the next »* | « Automatic Mode » utilisé : il sert à programmer des cartes en série | Arrêter le mode automatique et flasher avec la section **Download** |
| macOS demande « Allow accessory to connect? » | Sécurité USB de macOS (Apple Silicon) | Autoriser, après avoir vérifié le nom du périphérique |

## 5. Bilan

| Test | Résultat |
|---|---|
| Inspection visuelle | ✅ Conforme (résidu de flux près de l'USB-C à nettoyer) |
| Court-circuit des rails | ✅ Aucun |
| Énumération USB | ✅ Port série USB (CDC), pas de périphérique HID |
| Identification du MCU | ✅ 0x450, 2 MB, Cortex-M7 |
| Flash ArduCopter 4.7.2 | ✅ |
| 2 IMU ICM42688P | ✅ Détectées, EKF3 initialisé sur les deux |
| Baromètre DPS368 | ✅ |
| **OSD AT7456E** | ⏳ **À tester** (il faut un VTX ou un écran et une alimentation de labo) |

**Conclusion :** à ce stade, la carte se comporte comme une Matek authentique. Le test de l'OSD reste à faire. C'est le défaut signalé sur les contrefaçons, donc la carte n'est pas encore validée définitivement.

## 6. Reste à faire

- [ ] Tester l'OSD : VTX ou écran sur la pastille VTx, alimentation par Vbat limitée à environ 0,5 A
- [ ] Nettoyer le résidu de flux autour de l'USB-C (alcool isopropylique)
- [ ] Au montage : régler `FRAME_CLASS` et `FRAME_TYPE`, calibrer les accéléromètres, brancher le GPS avec boussole (Holybro Micro M10), insérer une carte microSD pour les logs

## Références

- Page produit Matek H743-SLIM-V4 (avis contrefaçon) : https://www.mateksys.com/?p=12864
- Revendeurs agréés Matek : https://www.mateksys.com/?page_id=1212
- STM32CubeProgrammer : https://www.st.com/en/development-tools/stm32cubeprog.html
- Firmware ArduPilot : https://firmware.ardupilot.org/Copter/stable/MatekH743/
- QGroundControl : https://github.com/mavlink/qgroundcontrol/releases
