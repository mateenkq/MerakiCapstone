#!/usr/bin/env python3
#
# GrovePi Library for using the Grove - I2C Motor Driver(http://www.seeedstudio.com/depot/Grove-I2C-Motor-Driver-p-907.html)
#
# The GrovePi connects the Raspberry Pi and Grove sensors.  You can learn more about GrovePi here:  http://www.dexterindustries.com/GrovePi
#
# Have a question about this library?  Ask on the forums here:  http://forum.dexterindustries.com/c/grovepi
#

# Released under the MIT license (http://choosealicense.com/licenses/mit/).
# For more information see https://github.com/DexterInd/GrovePi/blob/master/LICENSE

import time,sys
import RPi.GPIO as GPIO
import smbus
from di_sensors.easy_light_color_sensor import EasyLightColorSensor

# use the bus that matches your raspi version
rev = GPIO.RPI_REVISION
if rev == 2 or rev == 3:
    bus = smbus.SMBus(1)
else:
    bus = smbus.SMBus(0)

class motor_driver_load_cut:
    MotorSpeedSet             = 0x82
    PWMFrequenceSet           = 0x84
    DirectionSet              = 0xaa
    MotorSetA                 = 0xa1
    MotorSetB                 = 0xa5
    Nothing                   = 0x01
    EnableStepper             = 0x1a
    UnenableStepper           = 0x1b
    Stepernu                  = 0x1c
    I2CMotorDriverAdd         = 0x0f  #Set the address of the I2CMotorDriver

    def __init__(self,address=0x0f):
        self.I2CMotorDriverAdd=address

    #Maps speed from 0-100 to 0-255
    def map_vals(self,value, leftMin, leftMax, rightMin, rightMax):
        
#http://stackoverflow.com/questions/1969240/mapping-a-range-of-values-to-another
        # Figure out how 'wide' each range is
        leftSpan = leftMax - leftMin
        rightSpan = rightMax - rightMin
        # Convert the left range into a 0-1 range (float)
        valueScaled = float(value - leftMin) / float(leftSpan)
        # Convert the 0-1 range into a value in the right range.
        return int(rightMin + (valueScaled * rightSpan))

    #Set motor speed
    def MotorSpeedSetAB(self,MotorSpeedA,MotorSpeedB):
        MotorSpeedA=self.map_vals(MotorSpeedA,0,100,0,255)
        MotorSpeedB=self.map_vals(MotorSpeedB,0,100,0,255)
        bus.write_i2c_block_data(self.I2CMotorDriverAdd, self.MotorSpeedSet, [MotorSpeedA,MotorSpeedB])
        time.sleep(.02)

    #Set motor direction
    def MotorDirectionSet(self,Direction):
        bus.write_i2c_block_data(self.I2CMotorDriverAdd, self.DirectionSet, [Direction,0])
        time.sleep(.02)

    def run_dispense(self):
        try:
            self.MotorSpeedSetAB(0,69)
            self.MotorDirectionSet(0b0101)
            time.sleep(.08)
            my_lcs = EasyLightColorSensor(led_state = True)
            def is_black():
                red, green, blue, clear = my_lcs.safe_raw_colors()
##                print(sum([red, green, blue]) / 3)
                #Print the values
                return sum([red, green, blue]) / 3 < 0.035
            time.sleep(.05)
            self.MotorSpeedSetAB(0,0)
            self.MotorSpeedSetAB(0,100)     #defines the speed of motor 1 and motor 2;
            self.MotorDirectionSet(0b0101)  #"0b1010" defines the output polarity, "10" means the M+ is "positive" while the M- is "negtive
            while True:
                if is_black():
                    break
            time.sleep(0.05)
            self.MotorSpeedSetAB(0,0)
            #FORWARD
            self.MotorSpeedSetAB(100,0)     #defines the speed of motor 1 and motor 2;
            self.MotorDirectionSet(0b1010)  #"0b1010" defines the output polarity, "10" means the M+ is "positive" while the M- is "negtive"
            time.sleep(2.78)
            self.MotorSpeedSetAB(0,0)
            self.MotorSpeedSetAB(100,0)
            self.MotorDirectionSet(0b0101)  #0b0101  Rotating in the opposite direction
            time.sleep(3.3)
            self.MotorSpeedSetAB(0,0)
            print('done cutting')
            self.MotorSpeedSetAB(0,0)
        except IOError:
            print("Unable to find the motor driver, check the addrees and press reset on the motor driver and try again")

    def rollforward(self):
        try:
            self.MotorSpeedSetAB(0,69)
            self.MotorDirectionSet(0b0101)
            time.sleep(0.25)
            self.MotorSpeedSetAB(0,0)
        except IOError:
            print("Unable to find the motor driver, check the addrees and press reset on the motor driver and try again")

    def rollback(self):
        try:
            self.MotorSpeedSetAB(0,69)
            self.MotorDirectionSet(0b1010)
            time.sleep(5)
            self.MotorSpeedSetAB(0,0)
        except IOError:
            print("Unable to find the motor driver, check the addrees and press reset on the motor driver and try again")
            

load_cut = motor_driver_load_cut()

            
            
