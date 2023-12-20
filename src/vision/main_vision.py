import socket
import logging
import numpy as np
import cv2
import struct

# ---------------------------------------------------------------------------- #
#                               Class Definition                               #
# ---------------------------------------------------------------------------- #

class ClientSocket:
    def __init__(self, socket_path: str, logger_name: str):
        self.logger = logging.getLogger(logger_name)
        self.Socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.Socket.connect(socket_path)
        self.logger.info("Connected to UNIX Socket")

    def send_bytes(self, bytes):
        self.Socket.sendall(bytes)

# ----------------------- Sending marker (VisionSocket) ---------------------- #
def send_marker(x:float, theta:float, phi:float, id: int):
    """ Sending marker infos to brain

    Args:
        marker (dict): Dict in form of {"x" : float(distance to marker), "theta" : float(angle on plan), "phi" : float(angle on y), "id": marker number
    """
    global VisionSocket
    bytes = bytearray(16)
    struct.pack_into("f", bytes, 0, x)
    struct.pack_into("f", bytes, 4, theta)
    struct.pack_into("f", bytes, 8, phi)
    struct.pack_into("i", bytes, 12, id)

    VisionSocket.send_bytes(bytes)

# ---------------------------------------------------------------------------- #
#                                     Code                                     #
# ---------------------------------------------------------------------------- #

def mainloop():
    logging.basicConfig(level=logging.DEBUG)

    # Socket used to send data to brain
    global VisionSocket
    VisionSocket = ClientSocket("vision.sock", "VisionSocket")
    
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
    marker_size = 0.05  # Par exemple, un marqueur de 7cm

    # Charger la vidéo en direct depuis la caméra (changez le numéro de la caméra si nécessaire)
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

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
            liste_aruco=[]
            for i in range(len(ids)):
                marker_points = np.array([[-marker_size/2, marker_size/2, 0],
                                        [marker_size/2, marker_size/2, 0],
                                        [marker_size/2, -marker_size/2, 0],
                                        [-marker_size/2, -marker_size/2, 0]], dtype=np.float32)
                a, rvec, tvec = cv2.solvePnP(marker_points, corners[i], cameraMatrix, distCoeffs, False, cv2.SOLVEPNP_IPPE_SQUARE)
                x = tvec[2][0]  # Distance en mètres
                theta = np.arctan((tvec[0][0])/ tvec[2][0]) # Angle avec la caméra
                phi = rvec[2][0] +np.pi/2 # Orientation capteur
                liste_aruco.append((x,theta,phi,ids[i][0]))

            """ The nearest marker is send """
            x, theta, phi, id = min(liste_aruco)
            send_marker(x, theta, phi, id)
        else:
            send_marker(0, 0, 0, -1)

if __name__ == "__main__":
   mainloop()