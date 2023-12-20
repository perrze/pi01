import logging
from common import *
import time

def test_forward(driver: MotorDriver, speed: float=1, duration: float=3):
    logging.info(f"[TEST] Forward at speed ({speed}) for {duration:.1f} seconds")
    #Left
    driver.set_left(abs(100*speed), 1)
    # Right
    driver.set_right(abs(100*speed), 1)
    
    time.sleep(duration)

def test_backward(driver: MotorDriver, speed: float=1, duration: float=3):
    logging.info(f"[TEST] Forward at speed ({speed}) for {duration:.1f} seconds")
    #Left
    driver.set_left(abs(100*speed), -1)
    # Right
    driver.set_right(abs(100*speed), -1)
    
    time.sleep(duration)    

def run_tests(driver: MotorDriver):
    test_forward(driver, 1, 3)
    driver.stop()
    test_backward(driver, 1, 3)
    driver.stop()

def main():
    setup_loggers()
    main_logger = setup_logger("BrainInt")
    driver = MotorDriver()
    
    try:
        run_tests(driver)
    except KeyboardInterrupt:
        driver.stop()
    except Exception as e:
        main_logger.error(e)
        driver.stop()
        raise e

    exit(0)

if __name__=='__main__':
    main()