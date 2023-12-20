# Installation d'un OS sur Raspberry Pi
## Pré-requis
1. Support d'installation (Clé USB ou carte MicroSD)
2. Installeur officiel Raspberry Pi OS


## Utilisation de l'installeur
La fondation Raspberry fournit un exécutable (Windows mais pas que) tout-en-un permettant de télécharger une image OS, de la configurer et de l'écrire sur le suppport d'installation automatiquement.

### 1) Choix de l'image disque

Il est possible de choisir entre plusieurs images disques. Ces différentes images sont fournies avec différentes options.
Dans notre cas nous ne souhaitons pas utiliser d'interface de bureau.
L'image choisie est donc: `Raspberry Pi OS Lite (64 bits)`

### 2) Configuration de l'image disque

Il est nécesaire de remplir différents champs : 
1. Nom d'hôte (Nom de la carte)
2. Configuration du SSH
    1. On choisi de l'activer pour accéder à la carte à distance
    2. On configure une clé publique afin de pouvoir s'y connecter sans mot de passe 
3. Le compte par défaut de la carte
    User: **pi** Password : **admin** 
4. Configuration du réseau WiFi
    On ne configure rien ici car les paramètres utilisés pour se connecter à Campus Telecom ne sont pas pas pris en compte dasn l'installeur
5. Configuration du type de clavier (fr)


### 3) Ecriture de l'image
On choisit le bon support d'installation pour écrire notre image configurée. (Ici la clé USB)

## Configuration du réseau Wi-Fi de Telecom
Afin de pouvoir accéder au réseau Telecom Campus, notre carte possède ses identifiants propres.  
On place dans la partition de boot (/boot) un fichier tp-2021.pem comprenant le certificat 802.X root de Telecom (Pour authentifier le réseau).
On écrit le fichier de conf dans /boot/wpa_supplicant.conf:
```conf
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=FR

network={
    ssid="Campus-Telecom"
    scan_ssid=1
    key_mgmt=WPA-EAP
    ca_cert="/boot/tp-2021.pem"
    eap=TTLS
    identity="robotpi-01.enst.fr"
    password="<mot de passe>"
    phase2="auth=PAP"
}
```

## Se connecter à la carte
Une fois la clé USB branchée et la carte initialisée, en étant connecté au réseau Telecom-Campus, on peut s'y connecter via:  
`ssh -i <chemin vers la clé> pi@robotpi-01.enst.fr`
