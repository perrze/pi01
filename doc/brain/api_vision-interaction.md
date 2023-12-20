
numerosqui representent des ordes
requette 
et cest a moi de dire au hardware que faire de facon szstematique ou pas 
# vision interaction:

## 1) infos recues:

### Numero du QR code      
    format: integer <number>    
     vars:       
       - Number: integer ([1,2,3,4,5,6...])     
     Permet a un client d'envoyer le contenu ou lordre donné par le QR code qui est un nombre format souhaité 

## 2) infos énvoyées à vision
    Aucune réponse est envoyée au client ou une réponse pour valider la réception de l'information 

## 3) Traitement de l'information recu par le QR code
Le brain traduit l'information recu par le QR code qui est un chiffres en lorde equivalent et envoit cet ordre là à la partie Hardware.
## 3) Infos envoyées à Hardware
exemple: tourner à droite.
### Position:
Nombre de flotants 3: envoyés dans un seul message 
 format: del <dx> <dy> <dr>    
     vars:       
       - position: float ([-1,+1])    
       - unité: mètre  
     Permmettent de preciser la position du robot dans un plan 
   