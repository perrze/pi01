## Setup camera

## Récupération du nom
On utilise la commande `lsusb` afin de lister les périphériques connectés. En utilisant la commande avant et après branchement de la caméra on obtient le nom: 
>`Suyin LENCO`

Une ligne ressemble à  
```Bus 001 Device 005: ID 1e45:8022 Suyin LENCO```  
Ici on obtient le numéro du device: `005`

Pour tester la webcam on peut utiliser `ffmpeg`