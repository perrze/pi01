from common import *
import time
from mpu6050 import mpu6050

def mainloop(driver: MotorDriver, accelerometer: mpu6050):
    logger = setup_logger("mainloop")
    while True:
        accel_data = accelerometer.get_accel_data(True)
        gyro_data = accelerometer.get_gyro_data()
        logger.info(f"accel_data: {accel_data} | gyro_data: {gyro_data}")
        forward = clamp(1, -1, 1)
        
        speed = clamp(0.4, 0, 1)
        left = clamp(forward, -1, 1)
        right = clamp(forward, -1, 1)

        #Left
        driver.set_left(left*speed)
        # Right
        driver.set_right(right*speed)
        time.sleep(1/1000)

def main():
    setup_loggers()
    main_logger = setup_logger("main")
    driver = MotorDriver()
    accelerometer = mpu6050(0x68)
    # Low pass filter
    accelerometer.set_filter_range(mpu6050.FILTER_BW_5)
    
    while True:
        try:
            mainloop(driver, accelerometer)
            break
        except KeyboardInterrupt:
            break
        except Exception as e:
            main_logger.error(e)
            driver.stop()
            raise e
    driver.stop()

if __name__=='__main__':
    main()