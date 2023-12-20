import socket
import struct
from PCA9685 import PCA9685
import logging
import socket
import struct
import threading
import math
import time
from common import *

class Config:
    hardware_socket_path = "hardware.sock"

class HardwareSocket:
    def __init__(self):
        self.logger = setup_logger("Hardware")
        self.socket = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
        self.logger.debug("Connecting socket...")
        while True:
            try:
                self.socket.connect(Config.hardware_socket_path)
                self.logger.info("Connection success")
                break
            except socket.timeout:
                self.logger.warn("timeout")
                continue
            except Exception as e:
                self.logger.error(e)
                raise e
        self.forback = 0
        self.rotation = 0
        # This flag is used to stop the listening thread
        self.should_stop = False
    
    def listen(self):
        self.logger.debug("Entering listen")
        while not self.should_stop:
            data = self.socket.recv(8)
            if not data:
                # If the data is empty, the connection was closed by the host
                break
            forback, rotation = struct.unpack("ff", data)
            # TODO: An issue may occur if the data is read while partially written
            self.forback = forback
            self.rotation = rotation
        
        if not self.should_stop:
            # If we exited the loop because of a broken pipe, we try to reconnect
            # We might want to introduce either a timout or a max number of tries
            self.listen()

    def stop(self):
        self.should_stop = True
        # We need to close the connection to avoid a deadlock
        if self.socket:
            self.socket.close()    

def mainloop(driver: MotorDriver, hardware_socket: HardwareSocket):
    while True:
        x, y = clamp(hardware_socket.forback, -1, 1), clamp(hardware_socket.rotation, -1, 1)
        speed = clamp(math.sqrt(x**2 + y**2), 0, 1)
        angle = -math.atan2(y, x)/math.pi
        left = clamp(2-abs(4*angle+1), -1, 1)
        right = clamp(2-abs(4*angle-1), -1, 1)

        #Left
        driver.set_left(left*speed)
        # Right
        driver.set_right(right*speed)

def main():
    setup_loggers()
    main_logger = setup_logger("BrainInt")
    
    driver = MotorDriver()
    hardware_socket = HardwareSocket()
    
    hardware_socket.logger.debug("Thread Listening")
    hardware_listening = threading.Thread(target=hardware_socket.listen, args=())
    hardware_listening.start()
    while True:
        try:
            mainloop(driver, hardware_socket)
            break
        except KeyboardInterrupt:
            break
        except Exception as e:
            main_logger.error(e)
            driver.stop()
            # TODO: Don't raise in production, continue instead
            raise e

    driver.stop()
    hardware_socket.stop()
    hardware_listening.join()

if __name__=='__main__':
    main()