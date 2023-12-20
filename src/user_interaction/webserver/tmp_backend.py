#!/usr/bin/env python
# This script aims to control the user interface for the qar project

# ---------------------------------------------------------------------------- #
#                                  Websockets                                  #
# ---------------------------------------------------------------------------- #
# The websocket is used to send order to the server faster than via HTTP

import asyncio
from websockets.server import serve
import json
import socket
import logging
import time
import os
import cv2


async def receiveFromUser(websocket):
    ws_logger = logging.getLogger("UIWebSocket")
    
    async for message in websocket:
        # ws_logger.info(message)
        data=json.loads(message)
        
        send={"type": "error", "content": "Bad type received"}
        await websocket.send(json.dumps(send))

async def opencv_mainloop(websocket):
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(dictionary, parameters)

    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Détecter les marqueurs ArUco dans l'image
        corners, ids, rejected = detector.detectMarkers(gray)
        print(ids)
        if ids is not None:
            send = {"ids": ids}
            await websocket.send(json.dumps(send))
            cv2.aruco.drawDetectedMarkers(gray, corners, ids)
        # cv2.imshow("markers", gray)
        if cv2.waitKey(1) & 0xFF == 27:
            break

# ---------------------------------------------------------------------------- #
#                                  UNIX Socket                                 #
# ---------------------------------------------------------------------------- #

async def app():
    logging.basicConfig(level=logging.INFO)
        
    # Always listen to Websocket
    async with connect(receiveFromUser,"",8765) as websocket:
        await opencv_mainloop(websocket)
        await asyncio.Future()
    
if __name__ == "__main__" :
    asyncio.run(app()) 
    