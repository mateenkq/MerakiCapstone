
import grove_i2c_motor_driver
import time
from di_sensors.easy_light_color_sensor import EasyLightColorSensor

def rollforward():
        try:

                m= grove_i2c_motor_driver.motor_driver()
                m.MotorSpeedSetAB(0,69)
                m.MotorDirectionSet(0b0101)
                time.sleep(0.25)
                m.MotorSpeedSetAB(0,0)

                
        except IOError:
                print("Unable to find the motor driver, check the addrees and press reset on the motor driver and try again")
	
