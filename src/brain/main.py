import time
import logging
import json
import threading
import socket
import os
import math
import struct
import numpy as np
from vcgencmd import Vcgencmd

#Le main dans brain cest the first end of communication dans le tunnel
# ---------------------------------------------------------------------------- #
#                                    Logging                                   #
# ---------------------------------------------------------------------------- #
class ColoredFormatter(logging.Formatter):
    """Logging Formatter to add pretty colors and formatting"""
    green = "\x1b[32m"
    red = "\x1b[91m"
    grey = "\x1b[37m"
    yellow = "\x1b[33m"
    bold_red = "\x1b[31m"
    reset = "\x1b[0m"
    format = "%(name)s %(message)s (%(filename)s:%(lineno)d)"

    singleton = None

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def setup_logger(name: str):
    """Should be called instead of the first call to logging.getLogger(name)"""
    ch = logging.StreamHandler()
    ch.setFormatter(ColoredFormatter.singleton)

    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    log.addHandler(ch)
    return log

def setup_loggers():
    """Removes the default handler of the root logger.
    It prevents double logging
    """
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger().removeHandler(logging.getLogger().handlers[0])
    ColoredFormatter.singleton = ColoredFormatter()

# ---------------------------------------------------------------------------- #
#                           Socket classes definition                          #
# ---------------------------------------------------------------------------- #

class Socket:
    """Mother class implementing functions relative to Unix Socket    """
    def __init__(self,socket_path:str,logger:str):
        """Initialize Socket
        
        Args:
            socket_path (str): File path to the unix socket
            logger (str): Name of the logger to log to
        """
        self.logger = setup_logger(logger)
        self.Socket = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
        self.Socket.bind(socket_path)
        self.Socket.listen(1)   # 1 means that we listen to only one connection
        self.connection:socket.socket = None
        # This flag is used to stop the listening thread
        self.should_stop = False
    
    def listen(self):
        self.logger.info("Waiting for unix socket connection")
        # We may want to increase the timeout to avoid spamming the logs
        self.Socket.settimeout(0.5)
        while not self.should_stop:
            try:
                self.connection,_ = self.Socket.accept()
                return True
            except socket.timeout:
                # This is fine, we just wait again for a connection
                continue
            except Exception as e:
                # This will never happen, except for a critical error
                # We might want to end the whole program at this point
                self.logger.critical(e)
                self.should_stop = True
                return False

    def stop(self):
        self.should_stop = True
        # We need to close the connection to avoid a deadlock
        if self.connection:
            self.connection.close()
    
    def send(self, response: str):
        pass

class UIDataSocket(Socket):
    """Class implementing functions relative to Unix Socket with UI
    """
    def __init__(self, socket_path: str, logger: str):
        """Initialize UIDataSocket
        
        Args:
            socket_path (str): File path to the ui unix socket
            logger (str): Name of the logger to log to
        """
        Socket.__init__(self, socket_path, logger)
        self.forback = 0.0
        self.rotation = 0.0       
        self.lastForback = 0.0
        self.lastRotation = 0.0 
    
    def listen(self):
        """Get data sent on the UNIX Socketx
        """
        connection_success = Socket.listen(self)
        if not connection_success:
            return
        self.logger.debug("Entering listen")
        while not self.should_stop:
            data = (self.connection.recv(1024)).decode("utf-8")
            # self.logger.debug("Request received: " + data)
            data = data.split()
            self.forback = float(data[0])
            self.rotation = float(data[1])
    
    def send(self, response: str):
        self.connection.sendall(response.encode("utf-8"))        
        
class UIControlSocket(Socket):
    """Class implementing functions relative to Unix Socket with UI
    """
    def __init__(self, socket_path: str, logger: str):
        """Initialize UIControlSocket
        
        Args:
            socket_path (str): File path to the ui unix socket
            logger (str): Name of the logger to log to
        """
        super().__init__(socket_path,logger)
        self.mode = "manual"
        self.max_speed = 1
        self.autonomous = None
        self.switched_mode = False
        
    def applyAction(self, data: dict):
        """Apply the action specified in JSON send by UIControlSocket

        Args:
            data (dict): A dictionnary of data
        """
        if (data["action"] == "changeMode"):
                self.logger.debug("Changing mode to: {}".format(data["mode"]))
                self.mode = data["mode"]
                self.autonomous.currentState = Autonomous.ST_DO_NOTHING
                self.switched_mode = True
        elif data["action"] == "setMaxSpeed":
            speed = float(data["speed"])
            self.max_speed = speed/100
    
    def listen(self):
        """Get data for the control pane of UIControlSocket
        """
        connection_success = Socket.listen(self)
        if not connection_success:
            return
        self.logger.debug("Entering listen")
        while not self.should_stop:
            data = (self.connection.recv(1024)).decode("utf-8")
            # self.logger.debug("Request received: " + data)
            data = json.loads(data)
            self.applyAction(data)
    
    def send(self,response:str):
        self.connection.sendall(response.encode("utf-8")) 

class VisionSocket(Socket):
    """Class implementing functions relative to Unix Socket with vision
    """
    def __init__(self, socket_path: str, logger: str):
        """Initialize vision 
        
        Args:
            socket_path (str): File path to the vision unix socket
            logger (str): Name of the logger to log to
        """
        Socket.__init__(self, socket_path, logger) # Calling the parent constructor
        # Parameters set by vision
        self.x = np.inf
        self.theta = 0.0
        self.phi = 0.0
        self.id = -1
        
        self.last_valid_x = np.inf
        self.last_valid_theta = 0
        self.last_valid_phi = 0
        self.last_valid_id = -1
        self.last_valid_time = 0
    
    def listen(self,ui_control_socket : UIControlSocket):
        """Get data sent on the UNIX Socketx
        """
        connection_success = Socket.listen(self)
        if not connection_success:
            return
        self.logger.debug("Entering listen")
        while not self.should_stop:
            data = self.connection.recv(16) # waits
            if not data:
                continue
            x, theta, phi, id = struct.unpack("fffi", data)
            self.id = id
            self.theta = theta
            self.phi = phi
            self.x = x
            if id>=0:
                self.last_valid_x = x
                self.last_valid_theta = theta
                self.last_valid_id = id
                self.last_valid_phi = phi
                self.last_valid_time = time.time()
            
            if ui_control_socket != None:
                response = {
                    "type" : "marker",
                    "id" : id,
                    "x" : x,
                    "theta" : theta,
                    "phi" : phi
                }
                ui_control_socket.send(json.dumps(response))

class HardwareSocket(Socket):
    def __init__(self):
        """Socket to send data to the hardware
        """
        Socket.__init__(self, Config.hardware_socket_path, "Hardware")
        self.max_speed = 1
    
    def listen(self):
        """Get data sent on the UNIX Socketx
        """
        connection_success = Socket.listen(self)
        if not connection_success:
            # Here the connection to the hardware raised an unknown exception
            # Handling exceptions in the parent class is less verbose, therefore
            # we don't propagate the exception but a boolean instead
            return
        
        self.logger.debug("Entering listen")
        while not self.should_stop:
            # The final data is unlikely to be a string, but
            # leaving this for now
            data = (self.connection.recv(1024)).decode("utf-8")
            if not data:
                # If the data is empty, the connection was closed by the client
                break
        if not self.should_stop:
            # If we exited the loop because of a broken pipe, we try to reconnect
            # We might want to introduce either a timout or a max number of tries
            self.listen()
    
    def send(self, forback: float, rotation: float) -> bool:
        if not self.connection:
            # self.logger.error("No connection to hardware")
            return False
        bytes = bytearray(8)
        struct.pack_into("f", bytes, 0, forback*self.max_speed)
        struct.pack_into("f", bytes, 4, rotation*self.max_speed)
        try:
            # This may fail if the client closed the connection
            self.connection.sendall(bytes)
        except BrokenPipeError:
            self.logger.error("Failed to send data to hardware, broken pipe")
            return False
        return True
    
# ---------------------------------------------------------------------------- #
#                                 Logic of calc                                #
# ---------------------------------------------------------------------------- #

class Specs:
    # Max speed in m/s
    # Determined empirically (dummy value for now)
    max_speed = 10.

    # Max rotation speed in rad/s
    # Determined empirically (dummy value for now)
    max_rotation_speed = 10.

class Config:
    data_socket_path = "ui_data.sock"
    control_socket_path = "ui_control.sock"
    vision_socket_path = "vision.sock"
    hardware_socket_path = "hardware.sock"

    socket_paths = (data_socket_path, control_socket_path,
                    vision_socket_path, hardware_socket_path)

def check_power(vcgm: Vcgencmd, ui_control_socket: UIControlSocket):
    is_throttled = vcgm.get_throttled()["breakdown"]["2"]
    if is_throttled:
        order = {
            "type": "under-voltage"
        }
        ui_control_socket.send(json.dumps(order))

def check_health(vcgm: Vcgencmd, ui_control_socket: UIControlSocket):
    check_power(vcgm, ui_control_socket)

def calculate_from_ui(ui_data_socket : UIDataSocket, hardware_socket : HardwareSocket, ui_control_socket : UIControlSocket):
    """Calculate and send the deltas to hardware from the data received from the UI

    Args:
        ui_data_socket (UIDataSocket): Socket to get the data from
        hardware_socket (HardwareSocket): Socket to send the data to
    """
    brain_logger = logging.getLogger("BrainInt")
    forback = ui_data_socket.forback
    rotation = ui_data_socket.rotation
    if (ui_data_socket.forback != ui_data_socket.lastForback 
        or ui_data_socket.rotation != ui_data_socket.lastRotation):
        # brain_logger.debug("Sent to HW:" + 
        #                   "Forback=" + str(ui_data_socket.forback) + 
        #                   "Rotation=" + str(ui_data_socket.rotation))
        ui_data_socket.lastForback = forback
        ui_data_socket.lastRotation = rotation
        hardware_socket.send(forback, rotation)

def clamp(x, x_min, x_max):
    return min(max(x, x_min), x_max)

class Autonomous:
    ROTATION_SPEED = 0.5
    ROTATION_SLEEP = 0.1
    CORRECTION_ROTATION_SLEEP = 0.1
    
    FORWARD_SPEED = 0.8
    FORWARD_SLEEP = 0.2
    
    WAITING_SLEEP = 0.4
    
    TIME_180 = 0.5
    TIME_90 = 0.5
    
    ST_DO_NOTHING = 0
    
    ST_LOOK_FOR_MARKER = 10
    ST_LOOK_FOR_MARKER_EVEN = 11
    ST_LOOK_FOR_MARKER_ODD = 12
    
    ST_COR_THETA = 20
    ST_COR_X = 21
    
    ST_FINISHED = 30
    ST_ON_EVEN_MARKER = 31
    ST_ON_ODD_MARKER = 32
    
    ST_FINISHED = 30
    ST_ON_EVEN_MARKER = 31
    ST_ON_ODD_MARKER = 32
    
    ST_BACKWARD = 50
    ST_GET_CLOSER_TO_MARKER = 51
    
    CT_COUNT_MAX = 4
    CT_ROTATING_SLEEP = 0.7
    CT_EPSILON_DEFAULT = (3*np.pi)/180

    CX_FORWARDING_SLEEP = 0.3
    CX_COUNT_MAX = 1
    
    BW_BACKWARDING_SLEEP = 2.0
    BW_SPEED = -0.5
    
    GCTM_SLEEP = 1.0
    GCTM_SPEED = 0.5
    
    def __init__(self,vision_socket: VisionSocket, hardware_socket: HardwareSocket):
        self.logger = setup_logger("AutonomousLogger")
        self.lastInstructionTime = 0.0
        self.currentTime = 0.0
        self.currentDeltaTimeWait = 0.0
        self.currentState = Autonomous.ST_DO_NOTHING
        self.vSock = vision_socket
        self.hSock = hardware_socket
        self.current_marker_type = "odd"
        self.validate = lambda x: x>=0
        self.milestones = {"reached_odd_marker" : True, "reached_even_marker" : True}
        
        
        # ----------------------------- look_for_marker() ---------------------------- #
        self.lfm_state = "waiting"
        
        # ---------------------------- correction_theta() ---------------------------- #
        self.ct_state = "waiting"
        self.ct_count_correction = 0
        
        # ------------------------------ correction_x() ------------------------------ #
        self.cx_state = "waiting"
        self.cx_count_correction = 0
        
        # -------------------------------- backward() -------------------------------- #
        self.bw_state = "waiting"
        
        # -------------------------- get_closer_to_marker() -------------------------- #
        self.gctm_state = "waiting"
                
    def look_for_marker(self):
        if self.validate(self.vSock.id): # Validate marker number
            self.lastInstructionTime = self.currentTime
            self.currentState = Autonomous.ST_COR_THETA
            self.hSock.send(0,0)
            self.lfm_state = "waiting"
            self.logger.warning("LFM to ST_COR_THETA")
            return
        
        if self.lfm_state == "waiting":
            if abs(self.currentTime - self.lastInstructionTime) > Autonomous.WAITING_SLEEP:
                self.hSock.send(0,Autonomous.ROTATION_SPEED)
                self.lastInstructionTime = self.currentTime
                self.lfm_state = "rotating"
        
        elif self.lfm_state == "rotating":
            if self.currentTime - self.lastInstructionTime > Autonomous.ROTATION_SLEEP:
                self.hSock.send(0,0)
                self.lastInstructionTime = self.currentTime
                self.lfm_state = "waiting"

    def correction_theta(self, epsilon: float = CT_EPSILON_DEFAULT):
        if (abs(self.vSock.last_valid_time-self.currentTime)>2):
            self.lastInstructionTime = self.currentTime
            self.currentState = Autonomous.ST_LOOK_FOR_MARKER
            self.ct_state = "waiting"
            self.ct_count_correction = 0
            self.hSock.send(0,0)
            self.logger.warning(f"Marker lost, falling back to LOOK_FOR_MARKER")
            return
        
        if (self.ct_count_correction >= Autonomous.CT_COUNT_MAX 
            or np.abs(self.vSock.last_valid_theta) <= epsilon):
            self.lastInstructionTime = self.currentTime
            self.currentState = Autonomous.ST_COR_X
            self.ct_state = "waiting"
            self.ct_count_correction = 0
            self.hSock.send(0,0)
            return
        
        if self.ct_state == "waiting":
            if abs(self.currentTime - self.lastInstructionTime) > Autonomous.WAITING_SLEEP:
                print(f"Correcting theta by {clamp(abs(self.vSock.last_valid_theta),0.4,1)*np.sign(self.vSock.last_valid_theta)}")
                print(f"Theta was actually {self.vSock.last_valid_theta}")
                self.hSock.send(0, clamp(abs(4*self.vSock.last_valid_theta),0.2,Autonomous.ROTATION_SPEED)*np.sign(self.vSock.last_valid_theta))
                self.lastInstructionTime = self.currentTime
                self.ct_count_correction += 1
                self.logger.warning(f"Correction theta {self.ct_count_correction}")
                self.ct_state = "rotating"
        
        if self.ct_state == "rotating":
            if self.currentTime - self.lastInstructionTime > Autonomous.CORRECTION_ROTATION_SLEEP:
                self.hSock.send(0,0)
                self.lastInstructionTime = self.currentTime
                self.ct_state = "waiting"


    def correction_x(self, distance : float):
        if np.abs(self.vSock.last_valid_x) <= distance:
            self.lastInstructionTime = self.currentTime 
            self.currentState = Autonomous.ST_GET_CLOSER_TO_MARKER
            self.cx_state = "waiting"
            self.cx_count_correction = 0
            self.hSock.send(0,0)
            self.logger.warning("ST_COR_X to ST_FINISHED")
            return
        
        if self.cx_count_correction > Autonomous.CX_COUNT_MAX:
            self.lastInstructionTime = self.currentTime
            self.currentState = Autonomous.ST_COR_THETA
            self.cx_state = "waiting"
            self.cx_count_correction = 0
            self.hSock.send(0,0)
            self.logger.warning("ST_COR_X to ST_COR_THETA")
            return
        
        if self.cx_state == "waiting":
            if abs(self.currentTime - self.lastInstructionTime) > Autonomous.FORWARD_SLEEP:
                self.hSock.send(clamp(self.vSock.last_valid_x/2,0.3,Autonomous.FORWARD_SPEED), 0)
                self.lastInstructionTime = self.currentTime
                self.cx_state = "forwarding"
                self.cx_count_correction += 1
        
        if self.cx_state == "forwarding":
            if abs(self.currentTime - self.lastInstructionTime) > Autonomous.WAITING_SLEEP:
                self.hSock.send(0,0)
                self.lastInstructionTime = self.currentTime
                self.cx_state = "waiting"
    
    def get_closer_to_marker(self):
        if self.gctm_state == "waiting":
            self.hSock.send(Autonomous.GCTM_SPEED, 0)
            self.lastInstructionTime = self.currentTime
            self.gctm_state = "forwarding"
                
        if self.gctm_state == "forwarding":
            if abs(self.currentTime - self.lastInstructionTime) > Autonomous.GCTM_SLEEP:
                self.hSock.send(0,0)
                if self.current_marker_type == "even":
                    self.lastInstructionTime = self.currentTime
                    self.currentState = Autonomous.ST_FINISHED
                    self.gctm_state = "waiting"                    
                else:
                    self.lastInstructionTime = self.currentTime
                    self.currentState = Autonomous.ST_BACKWARD
                    self.gctm_state = "waiting"
                    return        
                
    def backward(self):
        if self.bw_state == "waiting":
            self.hSock.send(Autonomous.BW_SPEED, 0)
            self.lastInstructionTime = self.currentTime
            self.bw_state = "backwarding"
                
        if self.bw_state == "backwarding":
            if abs(self.currentTime - self.lastInstructionTime) > Autonomous.BW_BACKWARDING_SLEEP:
                self.hSock.send(0,0)
                self.lastInstructionTime = self.currentTime
                if self.current_marker_type == "odd":
                    self.current_marker_type = "even"
                    self.validate = lambda x: x>=0 and x%2==0
                else:
                    self.current_marker_type = "odd"
                    self.validate = lambda x: x>=0 and x%2!=0
                self.currentState = Autonomous.ST_LOOK_FOR_MARKER
                self.bw_state = "waiting"
                return
        
def calculate_from_vision(autonomous: Autonomous):
    if autonomous.currentState == Autonomous.ST_DO_NOTHING:
        autonomous.vSock.last_valid_id = -1
        autonomous.vSock.id = -1
        autonomous.current_marker_type = "odd"
        autonomous.validate = lambda x: x>=0 and x%2!=0
        autonomous.currentState = Autonomous.ST_LOOK_FOR_MARKER
    
    elif autonomous.currentState == Autonomous.ST_LOOK_FOR_MARKER:
        autonomous.look_for_marker()
    
    elif autonomous.currentState == Autonomous.ST_LOOK_FOR_MARKER_EVEN:
        autonomous.validate = lambda x: x>=0 and x%2==0
        autonomous.look_for_marker()
    
    elif autonomous.currentState == Autonomous.ST_LOOK_FOR_MARKER_ODD:
        autonomous.validate = lambda x: x>=0 and x%2!=0
        autonomous.look_for_marker()
    
    elif autonomous.currentState == Autonomous.ST_COR_THETA:
        autonomous.correction_theta()
    
    elif autonomous.currentState == Autonomous.ST_COR_X:
        autonomous.correction_x(0.4)
    
    elif autonomous.currentState == Autonomous.ST_ON_EVEN_MARKER:
        autonomous.backward()
    
    elif autonomous.currentState == Autonomous.ST_GET_CLOSER_TO_MARKER:
        autonomous.get_closer_to_marker()
    
    elif autonomous.currentState == Autonomous.ST_BACKWARD:
        autonomous.backward()

def calculate(ui_data_socket: UIDataSocket, 
              ui_control_socket: UIControlSocket, 
              vision_socket: VisionSocket,
              hardware_socket: HardwareSocket):
    brain_logger = logging.getLogger("BrainInt")
    brain_logger.debug("Entering calculate")
    
    autonomous = Autonomous(vision_socket,hardware_socket)
    ui_control_socket.autonomous = autonomous
    # If change mode is pressed from UI the state  au autonomous is changed
    vcgm = Vcgencmd()
    last_health_check_time = time.time()
    while True:
        current_time = time.time()
        hardware_socket.max_speed = ui_control_socket.max_speed
        if current_time>last_health_check_time:
            last_health_check_time = current_time
            check_health(vcgm, ui_control_socket)
        if ui_control_socket.switched_mode:
            hardware_socket.send(0, 0)
            ui_control_socket.switched_mode = False
        if ui_control_socket.mode == "manual":
            calculate_from_ui(ui_data_socket, hardware_socket, ui_control_socket)
        else:
            autonomous.currentTime = current_time
            calculate_from_vision(autonomous)

def app():
    setup_loggers()
    brain_logger = setup_logger("BrainInt")
    
    # Removing all existing socket file
    # This is needed because the socket creation will throw an exception
    # if the file already exists
    for file in Config.socket_paths:
        if os.path.exists(file):
            os.unlink(file)
    
    ui_data_socket = UIDataSocket(Config.data_socket_path, "UIData")
    ui_control_socket = UIControlSocket(Config.control_socket_path, "UIControl")
    vision_socket = VisionSocket(Config.vision_socket_path,"Vision")
    hardware_socket = HardwareSocket()
    
    # We setup the listening threads
    # We need to do the listening in threads because calling listen stops the program
    # until a connection is made
    ui_data_socket.logger.debug("Thread Listening")
    ui_data_listening = threading.Thread(target=ui_data_socket.listen, args=())
    ui_data_listening.start()
    
    ui_control_socket.logger.debug("Thread Listening")
    ui_control_listening = threading.Thread(target=ui_control_socket.listen, args=())
    ui_control_listening.start()

    vision_socket.logger.debug("Thread Listening")
    vision_listening = threading.Thread(target=vision_socket.listen, args=(ui_control_socket,))
    vision_listening.start()

    hardware_socket.logger.debug("Thread Listening")
    hardware_listening = threading.Thread(target=hardware_socket.listen, args=())
    hardware_listening.start()
    
    

    # List of early exit flags
    # 0     normal exit
    # -1    CTRL-C catched
    # -2    division by zero
    early_exit_flag = 0
    while True:
        try:
            calculate(ui_data_socket, ui_control_socket, vision_socket, hardware_socket)
            break
        except KeyboardInterrupt:
            early_exit_flag = -1
            break
        except Exception as e:
            brain_logger.error(e)
            # TODO: Don't raise in production, continue instead
            raise e
            continue

    if not early_exit_flag:
        brain_logger.debug("The program exited normally")
    else:
        brain_logger.warning(f"The program exited early with code ({early_exit_flag})")

    ui_control_socket.stop()
    ui_data_socket.stop()
    hardware_socket.stop()
    vision_listening.stop()
    ui_data_listening.join()
    ui_control_listening.join()
    hardware_listening.join()
    vision_listening.join()
    for file in Config.socket_paths:
        if os.path.exists(file):
            os.unlink(file)
    exit(0)
    
        
if __name__ == "__main__" :
    app()
    
