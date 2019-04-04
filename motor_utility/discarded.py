import time,sys
import RPi.GPIO as GPIO
import smbus


# use the bus that matches your raspi version
rev = GPIO.RPI_REVISION
if rev == 2 or rev == 3:
    bus = smbus.SMBus(1)
else:
    bus = smbus.SMBus(0)

class motor_driver_nonad:

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
            valueScaled = float(value - leftMin) / float(leftSpan)              # Convert the left range into a 0-1 range (float)
            return int(rightMin + (valueScaled * rightSpan))            # Convert the 0-1 range into a value in the right range.
        
        def StepperStepset(self,stepnu): ##set the steps you want, if 255, the stepper will rotate continuely;
            bus.write_i2c_block_data(self.I2CMotorDriverAdd,self.Stepernu,[stepnu,self.Nothing])
            
        def StepperMotorEnable(self,Direction,motorspeed): ##set the steps you want, if 255, the stepper will rotate continuely;
            bus.write_i2c_block_data(self.I2CMotorDriverAdd,self.EnableStepper,[Direction,motorspeed])


        ##function to uneanble i2C motor drive to drive the stepper.

        def StepperMotorUnenable(self): ##set the steps you want, if 255, the stepper will rotate continuely;
            bus.write_i2c_block_data(self.I2CMotorDriverAdd,self.UnenableStepper,[self.Nothing,self.Nothing])


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


        def run_forward(self):
##            m= motor_driver(address=0x04)

            print('steps')
            self.StepperStepset(75)
            self.StepperMotorEnable(0, 2) #ennable the i2c motor driver a stepper.
            time.sleep(2) #Set this time and the steps of the rotating part of the slide 
        ##    m.MotorSpeedSetAB(0,0)
            self.StepperMotorUnenable()

        ##    time.sleep(2)  

        def run_backward(self):
            
            print('steps')
            self.StepperStepset(75);
            self.StepperMotorEnable(1, 2)
            time.sleep(2) #Keep the same values as above here except for the direction
        ##    m.MotorSpeedSetAB(0,0)
            self.StepperMotorUnenable()
            
            time.sleep(1)

nonad_motor = motor_driver_nonad(address=0x04)
##nonad_motor.run_forward()
##nonad_motor.run_backward()
