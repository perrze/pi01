# hardware interaction:


## 1) infos envoyées:

### Position:
Nombre de flotants 3: envoyés dans un seul message 
 format: del <dx> <dy> <dr>    
     vars:       
       - position: float ([-1,+1])    
       - unité: mètre  
     Permmettent de preciser la position du robot dans un plan 
   
## 2) infos recues:
### Acceleration: 
Nombre de flotants 3: envoyés dans un seul message 
 format: a <acceleration>
    vars:
     - acceleration: float ([-1,+1])
     - unité: métre\seconde.secondes
     permet de svoir l'acceleration du robot
### Rotation: 
Nombre de flotants 2: dx dy   
 format: ang <dx> <dy> 
    vars:
     - position: float ([-1,+1])
     permet de definir l'angle de rotation du robot