import cv2
import numpy as np
import time
import math

# Charger le dictionnaire ArUco
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)

# Créer un détecteur ArUco
parameters = cv2.aruco.DetectorParameters()

detector = cv2.aruco.ArucoDetector(dictionary, parameters)

#cameraMatrix = np.array([[632.15241386  , 0.   ,      337.525434  ],
# [  0.     ,    635.86738602, 280.66773411],
# [  0.      ,     0.    ,       1.        ]])
 # Exemple de matrice de caméra intrinsèque
#distCoeffs = np.array([[ 0.0217212  , 0.05185515 , 0.01173891 , 0.00810346, -0.31523066]])


donnees=np.load("calibration_params.npz")
cameraMatrix = donnees['cameraMatrix']
distCoeffs = donnees['distCoeffs']


# Définir la taille réelle du marqueur en mètres
marker_size = 0.05  # Par exemple, un marqueur de 10 cm

# Charger la vidéo en direct depuis la caméra (changez le numéro de la caméra si nécessaire)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    #time.sleep(0.7)
    if not ret:
        break
    # Convertir l'image en niveaux de gris
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Détecter les marqueurs ArUco dans l'image
    corners, ids, rejected = detector.detectMarkers(gray)
    if ids is not None:
        for i in range(len(ids)):
            marker_points = np.array([[-marker_size/2, marker_size/2, 0],
                                      [marker_size/2, marker_size/2, 0],
                                      [marker_size/2, -marker_size/2, 0],
                                      [-marker_size/2, -marker_size/2, 0]], dtype=np.float32)
            a, rvec, tvec = cv2.solvePnP(marker_points, corners[i], cameraMatrix, distCoeffs, False, cv2.SOLVEPNP_IPPE_SQUARE)
            distance = tvec[2][0]  # Distance en mètres
            # distance = tvec[0][0][2]  # Distance en mètres
            # angle=math.atan((tvec[0][0][0])/ tvec[0][0][2])
            # Dessiner la distance sur l'image
            #cv2.putText(frame, f"Distance: {distance:.2f} m", (int(corners[i][0][0][0]), int(corners[i][0][0][1] - 10)),
            #            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            #cv2.putText(frame, f"angle: {angle:.2f} rad", (int(corners[i][0][0][0]), int(corners[i][0][0][1] - 50)),
            #            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            #cv2.putText(frame, "cornersx:"+ str(int(corners[i][0][:][0].mean()))+","+str(int(corners[i][0][:][1].mean())), (int(corners[i][0][0][0]), int(corners[i][0][0][1] + 30)),
            #            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            # cv2.putText(frame,f"rvec: {rvec[0][0][2]:.3f} rad", (int(corners[i][0][0][0]), int(corners[i][0][0][1] - 10)),
            #                         cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            # cv2.drawFrameAxes(frame, cameraMatrix, distCoeffs, rvec, tvec, 0.1)
            print("distance:", distance)

    # Afficher l'image avec les marqueurs et la distance estimée
    # cv2.imshow("ArUco Marker Detection", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # Appuyez sur la touche Esc pour quitter
        break

# Libérer la capture vidéo et fermer la fenêtre
cap.release()
cv2.destroyAllWindows()