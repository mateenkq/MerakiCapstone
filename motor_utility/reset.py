import grove_i2c_motor_driver
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_UP)
try:
	# You can initialize with a different address too: grove_i2c_motor_driver.motor_driver(address=0x0a)
	m= grove_i2c_motor_driver.motor_driver()
	
	
		#FORWARD
	#print("Begin movement forward")
	m.MotorSpeedSetAB(100,100)	#defines the speed of motor 1 and motor 2;
	m.MotorDirectionSet(0b0101)
	time.sleep(.1)
	m.MotorSpeedSetAB(0,0)	

except IOError:
	print("Unable to find the motor driver, check the addrees and press reset on the motor driver and try again")