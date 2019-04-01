import grove_i2c_motor_driver
import time
from di_sensors.easy_light_color_sensor import EasyLightColorSensor
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

def rollback():
        try:

                m= grove_i2c_motor_driver.motor_driver()
                m.MotorSpeedSetAB(0,69)
                m.MotorDirectionSet(0b1010)
                while GPIO.input(11) != GPIO.HIGH:
                    continue
                m.MotorSpeedSetAB(0,0)

                
        except IOError:
                print("Unable to find the motor driver, check the addrees and press reset on the motor driver and try again")
	
