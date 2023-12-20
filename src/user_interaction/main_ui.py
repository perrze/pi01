#!/usr/bin/env python
# This script aims to control the user interface for the jcar project

import asyncio
from websockets.server import serve
import json
import socket
import logging
import time
import os
import threading
import bcrypt

PASSWORD_NEEDED = False

# ---------------------------------------------------------------------------- #
#                                  UNIX Socket                                 #
# ---------------------------------------------------------------------------- #
class ClientSocket:
    """Client class for UNIX Socket used multiple times"""

    def __init__(self, socket_path: str, logger_name: str):
        """Constructor for ClientSocket which wait

        Args:
            socket_path (str): path to the file for the UNIX Socket
            logger_name (str): Name for the logger (from logging)
        """
        self.logger = logging.getLogger(
            logger_name
        )  # Get the logger and put it in the member data
        self.Socket = socket.socket(
            socket.AF_UNIX, socket.SOCK_STREAM
        )  # Create a Socket object
        while not (os.path.exists(socket_path)):
            pass  # While the socket server doesn't exist
        self.Socket.connect(socket_path)  # Bind the socket to the path
        self.logger.info("Connected to UNIX Socket")
        self.should_stop = False

        # use to prevent flooding the buffer of the socket
        self.lastForback = 0.0
        self.lastRotation = 0.0
        
        self.message = ""
        self.lastMessage = ""

    def listen(self):
        self.logger.debug("Entering listen")
        while not self.should_stop:
            self.message = (self.Socket.recv(1024)).decode("utf-8")
            
    def send(self, request: str):
        self.Socket.sendall(request.encode("utf-8"))


# ----------------------- Applying Order (UIDataSocket) ---------------------- #


def applyOrder(order: dict):
    """Sending order from websocket to UNIX socket

    Args:
        order (dict): Dict in form of {"rotation": float, "forback":float}
    """
    global DataSocket
    # Detect Modification of the Socket
    if (
        order["forback"] != DataSocket.lastForback
        or order["rotation"] != DataSocket.lastRotation
    ):
        request = str(order["forback"]) + " " + str(order["rotation"]) + "\n"
        DataSocket.lastForback = order["forback"]
        DataSocket.lastRotation = order["rotation"]
        DataSocket.send(request)


# --------------------- Applying Option (UiControlSocket) -------------------- #


def changeControlMode(data: dict):
    """Change the control mode of the robot

    Args:
        data (dict): the data dict sent by the user
    """
    ws_logger = logging.getLogger("UIWebSocket")
    global ControlSocket
    # Prevent errors whle handling user entered commands
    if data["mode"] in ("manual", "ia"):
        request = {"action": "changeMode", "mode": data["mode"]}
        # Dumping JSON to send it on the ControlSocket
        ControlSocket.send(json.dumps(request))
        ws_logger.info("Sent to control: {}".format(json.dumps(request)))

def set_max_speed(speed: float):
    global ControlSocket

    request = {"action": "setMaxSpeed", "speed": speed}

    ControlSocket.send(json.dumps(request))
    ws_logger = logging.getLogger("UIWebSocket")
    ws_logger.info("Sent to control: {}".format(json.dumps(request)))

def applyOption(option: str, data: dict):
    """Apply an option choosen by the user

    Args:
        option (str): What option to change
        data (dict): data dict sent by user
    """
    ws_logger = logging.getLogger("UIWebSocket")
    ws_logger.info("Applying option with data: {}".format(data))
    if option == "mode":
        ws_logger.info("Changing mode")
        changeControlMode(data)
    elif option == "max_speed":
        ws_logger.info("Changing speed to "+str(data["value"]))
        f = float(data["value"])
        if f is None:
            f = 0
        set_max_speed(f)


# ---------------------------------------------------------------------------- #
#                                  Websockets                                  #
# ---------------------------------------------------------------------------- #
# The websocket is used to send order to the server faster than via HTTP

async def receiveFromUser(websocket):
    
    """Receiving requests on websocket from the user

    Args:
        websocket (websockets):  A Websocket
    """
    ws_logger = logging.getLogger("UIWebSocket")
    
    if PASSWORD_NEEDED:
        password = await websocket.recv()
        salt =  b'$2b$12$Jhl26OvQrlZqC4SfNkAouu'
        goodPass = b'$2b$12$Jhl26OvQrlZqC4SfNkAouuD8OlmfunwfRpe5CYdLSh4fj3P7nXyLG'
        if bcrypt.hashpw(bytes(password,"utf-8"),salt) == goodPass:
            await websocket.send(json.dumps({"type" : "info", "message": "Access Granted"}))
        else:
            await websocket.close()
            return

    async for message in websocket:
        # ws_logger.info(message)
        data = json.loads(message)

        if data["type"] == "order":
            # if not (
            #     data["position"]["forback"] == 0 and data["position"]["rotation"] == 0
            # ):
                # ws_logger.info(
                #     "An order has been received: {}".format(data["position"])
                # )
            applyOrder(data["position"])
        elif data["type"] == "option":
            ws_logger.info(
                "An option to change has been received:{}".format(data["option"])
            )
            applyOption(data["option"], data["data"])
        elif data["type"] == "info":
            print("(INFO): {}".format(data["content"]))
        else:
            print("(ERROR): bad type")
            send = {"type": "error", "content": "Bad type received"}
            await websocket.send(json.dumps(send))

async def app():
    logging.basicConfig(level=logging.INFO)

    # Socket used to send data for forback and others
    global DataSocket
    DataSocket = ClientSocket("ui_data.sock", "DataSocket")
    time.sleep(0.5)
    # Socket used to tell brain whether its IA or UI
    global ControlSocket
    ControlSocket = ClientSocket("ui_control.sock", "ControlSocket")

    ControlSocket.logger.info("Thread Listening")
    control_listening = threading.Thread(target=ControlSocket.listen, args=())
    control_listening.start()

    # Always listen to Websocket
    async with serve(receiveFromUser, "", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":

    asyncio.run(app())
