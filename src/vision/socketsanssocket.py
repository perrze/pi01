import asyncio
import socket
import logging
import numpy as np
import cv2
import time

# Charger le dictionnaire ArUco
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)

# Créer un détecteur ArUco
parameters = cv2.aruco.DetectorParameters()

detector = cv2.aruco.ArucoDetector(dictionary, parameters)

#on récupère les paramètres de la caméra enregistrés à partir de calibrage_caméra.py
donnees=np.load("src/vision/calibration_params.npz")
cameraMatrix = donnees['cameraMatrix']
distCoeffs = donnees['distCoeffs']

# Définir la taille réelle du marqueur en mètres
marker_size = 0.07  # Par exemple, un marqueur de 7cm

# Charger la vidéo en direct depuis la caméra (changez le numéro de la caméra si nécessaire)
cap = cv2.VideoCapture("/dev/video0")

#init order
order={'x' : np.inf,'theta': 0 , 'phi' : 0,"id":1}
while True:
    # time.sleep(0.4)
    ret, frame = cap.read()
    if not ret:
        break
    # Convertir l'image en niveaux de gris
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Détecter les marqueurs ArUco dans l'image
    corners, ids, rejected = detector.detectMarkers(gray)
    if ids is not None:
        liste_aruco=[]
        for i in range(len(ids)):
            marker_points = np.array([[-marker_size/2, marker_size/2, 0],
                                      [marker_size/2, marker_size/2, 0],
                                      [marker_size/2, -marker_size/2, 0],
                                      [-marker_size/2, -marker_size/2, 0]], dtype=np.float32)
            a, rvec, tvec = cv2.solvePnP(marker_points, corners[i], cameraMatrix, distCoeffs, False, cv2.SOLVEPNP_IPPE_SQUARE)
            x = tvec[2][0]  # Distance en mètres
            theta =np.arctan((tvec[0][0])/ tvec[2][0]) + np.pi/2 #angle avec la caméra
            phi = rvec[2][0] +np.pi/2# orientation capteur
            liste_aruco.append((x,theta,phi,ids[i][0]))

        """ ON ENVOIE QUE LE MARQUEUR LE PLUS PROCHE"""
        x, theta, phi, id = min(liste_aruco)
        order['x'] = round(x, 3)
        order['theta'] = round(theta, 3)
        order['phi'] = round(phi, 3)
        order['id'] = id
        print(order)
        #applyOrder(order)
    if cv2.waitKey(1) & 0xFF == 27:
        break
