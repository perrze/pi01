import numpy as np
import cv2

def mainloop():
    # Charger le dictionnaire ArUco
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)

    # Créer un détecteur ArUco
    parameters = cv2.aruco.DetectorParameters()
    parameters.adaptiveThreshWinSizeMin = 21
    parameters.adaptiveThreshWinSizeMax = 40
    parameters.adaptiveThreshWinSizeStep = 2
    # parameters.adaptiveThreshConstant = 7
    # parameters.adaptiveThreshConstant = 0.4

    detector = cv2.aruco.ArucoDetector(dictionary, parameters)

    cap = cv2.VideoCapture(0)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    cap.set(cv2.CAP_PROP_EXPOSURE, -5)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # for threshold in range(parameters.adaptiveThreshWinSizeMin, parameters.adaptiveThreshWinSizeMax, parameters.adaptiveThreshWinSizeStep):
        #     frame_thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, threshold, -parameters.adaptiveThreshConstant)
        #     cv2.imshow(str(threshold), frame_thresh)

        # Détecter les marqueurs ArUco dans l'image
        corners, ids, rejected = detector.detectMarkers(gray)
        # cv2.aruco.drawDetectedMarkers(frame, corners, ids)
        # cv2.imshow("markers", frame)
        # cv2.imshow("gray", gray)
        # print(ids, rejected)
        # if cv2.waitKey(1) & 0xFF == 27:
        #     break
        print(ids)

if __name__ == "__main__":
   mainloop()
