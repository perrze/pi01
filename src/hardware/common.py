from PCA9685 import PCA9685
import logging
import math

class MotorDriver():
    def __init__(self):
        self.PWMA = 0
        self.AIN1 = 1
        self.AIN2 = 2
        self.PWMB = 5
        self.BIN1 = 3
        self.BIN2 = 4
        self.pwm = PCA9685(0x40, debug=False)
        self.pwm.setPWMFreq(50)

    
    def get_abs_speed(self, speed):
        return clamp(abs(100*speed), 0, 100)
    
    def set_left(self, speed:float):
        abs_speed = self.get_abs_speed(speed)
        self.pwm.setDutycycle(self.PWMA, abs_speed)
        if speed>0:
            self.pwm.setLevel(self.AIN1, 0)
            self.pwm.setLevel(self.AIN2, 1)
        else:
            self.pwm.setLevel(self.AIN1, 1)
            self.pwm.setLevel(self.AIN2, 0)
    
    def set_right(self, speed):
        abs_speed = self.get_abs_speed(speed)
        self.pwm.setDutycycle(self.PWMB, abs_speed)
        if speed>0:
            self.pwm.setLevel(self.BIN1, 0)
            self.pwm.setLevel(self.BIN2, 1)
        else:
            self.pwm.setLevel(self.BIN1, 1)
            self.pwm.setLevel(self.BIN2, 0)

    def stop(self):
        self.pwm.setDutycycle(self.PWMA, 0)
        self.pwm.setDutycycle(self.PWMB, 0)

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
    
def sign(x):
    return 1 if x>=0 else -1

def clamp(x, x_min, x_max):
    return min(max(x, x_min), x_max)