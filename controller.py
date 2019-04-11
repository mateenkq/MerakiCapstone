#!/usr/bin/env python3

import redis
import time
import queue
import datetime
from help import *
import os
import sys
import RPi.GPIO as GPIO
from motor_utility import load_cut, nonad_motor
import threading

print('starting')
##time.sleep(20)
print('ready')

#Medication dispensing availability time from the point the alarm goes off
#By default it is 3 hours
# TODO: dynamic snoozing
TIME_LIMIT = datetime.timedelta(0, 10800) 
reg = [] #medication regiment holder
later_reg = None #the regimen after the next one
Snooze_Count = 0 #Time that the user pressed the sleep button
temp_time = 0 #time register for snoozing
outer_time = 0 #time register for the overall period
right_time = 'N' #Is it the right time to dispense?
release = 0 #Time to release flag
non_adherence = 0 #Non adherence system flag
invalid_counter = 0 #This counter keeps track of how many invalid regimen is there
travel_counter = 0 # Keeps track of travel packs...just one for now
finished = False
TRAVEL_ALLOWED = False

DISPENSE = 11
SNOOZE = 13
TRAVEL = 7
LOAD = 11
LOAD_COMPLETE = 7
PROXIMITY = 10
GET_BACK = 13


redisClient = redis.Redis()
redisPublisher = redis.Redis()

pubsub = redisClient.pubsub()
pubsub.subscribe("Interface","wireless")



def listen():
    global Snooze_Count
    global temp_time
    global release
    global right_time
    global non_adherence
    global reg
    global invalid_counter
    global outer_time
    global later_reg
    global finished
    global TRAVEL_ALLOWED

    if len(reg) == 0:
        redisPublisher.publish("This is main","yes")
    try:
        for item in pubsub.listen():
            print(item)
            # These lines here ensure that the regimen main file received from Wireless module is valid
            if type(item['data']) is not int:
                item = str(item['data'], 'utf-8')
                if item == 'finished':
                    finished = True
                    reg = []
                    redisPublisher.publish("This is main","finished")
                    break
                if len(reg) == 0:
                    redisPublisher.publish("This is main","yes")
                if item == 'travel-ok':
                    TRAVEL_ALLOWED = True
                    continue
                    
                if item == 'waiting': # while the MQTT subscriber is still waiting for regimen from pharmacist
                    continue
                
                if item == 'new': # indicates that a new regimen is available
                    print('new')
                    reg = []
                    finished = True
                    break
##                    redisPublisher.publish("This is main","yes")
##                    continue

                next_dosage, next_x_2 = None, None
                regs = item.split(":")
                if len(regs) > 1:
                    next_dosage = regs[0]
                    next_x_2 = regs[1]
                    later_reg = next_x_2.split()
                else:
                    next_dosage = regs[0]
                    next_x_2 = None
                    later_reg = None
                
                redisPublisher.publish("This is main","next:" + next_dosage)
                temp_reg = next_dosage.split()
                print('Medication Regimen Received')
                
                if validate(int(temp_reg[0]), int(temp_reg[1]), int(temp_reg[2]), int(temp_reg[3]), int(temp_reg[4]), TIME_LIMIT) == 'N':
                    print('Medication Regimen is invalid')
                    invalid_counter += 1
                    redisPublisher.publish("This is main", "invalid")
    ##                break
                else:
                    print('Medication Regimen is valid')
                    reg = temp_reg
                    if invalid_counter > 0:
                        non_adherence = 1
                    redisPublisher.publish("This is main", "valid")
                    print(reg)
    ##                break
                
            else:
                continue
    except KeyboardInterrupt:
        pass


def run():
##    GPIO.setwarnings(False)
##    GPIO.setmode(GPIO.BOARD)
##    GPIO.setup(DISPENSE, GPIO.IN,pull_up_down=GPIO.PUD_DOWN) # defining dispense button
##    GPIO.setup(SNOOZE, GPIO.IN,pull_up_down=GPIO.PUD_DOWN) # defining snooze button
##    GPIO.setup(TRAVEL, GPIO.IN,pull_up_down=GPIO.PUD_DOWN) # defining travel pack button

    global Snooze_Count
    global temp_time
    global release
    global right_time
    global non_adherence
    global reg
    global invalid_counter
    global outer_time
    global later_reg
    global finished
    global TRAVEL_ALLOWED



##    if len(reg) == 0:
##        redisPublisher.publish("This is main","yes")
##
##    for item in pubsub.listen():
##        
##        # These lines here ensure that the regimen main file received from Wireless module is valid
##        if type(item['data']) is not int:
##            item = str(item['data'], 'utf-8')
##            redisPublisher.publish("This is main","yes")
##            
##            if item == 'waiting': # while the MQTT subscriber is still waiting for regimen from pharmacist
##                continue
##            
##            if item == 'new': # indicates that a new regimen is available
##                print('new')
##                redisPublisher.publish("This is main","yes")
##                continue
##            
##            redisPublisher.publish("This is main","next:" + item)
##            reg = item.split()
##            print('Medication Regimen Received')
##            
##            if validate(int(reg[0]), int(reg[1]), int(reg[2]), int(reg[3]), int(reg[4]), TIME_LIMIT) == 'N':
##                print('Medication Regimen is invalid')
##                invalid_counter += 1
##                redisPublisher.publish("This is main", "invalid")
####                break
##            else:
##                print('Medication Regimen is valid')
##                redisPublisher.publish("This is main", "valid")
##                print(reg)
##                break
##            
##        else:
##            continue

##    while invalid_counter > 0:
##        redisPublisher.publish("This is main","discarding")
##        #These lines storages all the missed medication into the storage space
##        print('Activate the non-adherence mechanism for invalid medication')
##        nonad_motor.run_forward()
##        load_cut.run_dispense()
##        nonad_motor.run_backward()
##        invalid_counter -= 1


    while finished == False:
        ##start new
        while invalid_counter > 0:
            while non_adherence == 1:
                redisPublisher.publish("This is main","discarding")
                #These lines storages all the missed medication into the storage space
                print('Activate the non-adherence mechanism for invalid medication')
                nonad_motor.run_forward()
                load_cut.run_dispense()
                time.sleep(1)
                nonad_motor.run_backward()
                invalid_counter -= 1
##                redisPublisher.publish("This is main","Nonad-run") #send the non-adherence data
                if invalid_counter == 0:
                    non_adherence = 0  #Reset the non adherence flag

        ##finish new

        
        if GPIO.input(TRAVEL) == GPIO.HIGH:
            redisPublisher.publish("This is main", "travel")
            time.sleep(1)
            if TRAVEL_ALLOWED == True:
                redisPublisher.publish("This is main", "dispense-travel")
                redisPublisher.publish("This is main","Medrun")
                load_cut.run_dispense()
                release = 0 # Set the release flag back to 0
                reg = []
                TRAVEL_ALLOWED = False
                redisPublisher.publish("This is main","yes")
##            break

        current_reg = datetime.datetime(2099,12, 31)
        if len(reg) > 0:
            current_reg = datetime.datetime(*[int(i) for i in reg])
        if datetime.datetime.now() > current_reg:
            print(reg)
            redisPublisher.publish("This is main","can_dispense")
            if release == 0:
                release = 1
##                os.system("mpg123 http://ice1.somafm.com/u80s-128-mp3 &")
##                current_reg = datetime.datetime(2099,12, 31)
                
        if release == 1:
            time_to_next = TIME_LIMIT
            if later_reg is not None:
                next_time = datetime.datetime(*[int(i) for i in later_reg])
                time_to_next = next_time - current_reg

            current_limit = min(TIME_LIMIT, time_to_next)
            outer_time = (time.time())//60
            #Alarm the User
            #Now it is in state 5

            snooze_time = current_limit/6
            if check_expiry(datetime.datetime.now(), current_reg, current_limit):
                non_adherence = 1
            
            elif GPIO.input(DISPENSE) == GPIO.HIGH:
                # If the user pressed the release button, release medication and go to state 6
                print('Release Button Pressed')
                print("Pill is dispensing")
                os.system('killall -9 mpg123')
                redisPublisher.publish("This is main","dispensing")
                load_cut.run_dispense()
                redisPublisher.publish("This is main","Medrun")
                non_adherence = 0
                release = 0 # Set the release flag back to 0
                reg = []
                current_reg = datetime.datetime(2099,12, 31)
                redisPublisher.publish("This is main","yes")
                Snooze_Count = 0
                print('abcde')
##                break

            elif GPIO.input(SNOOZE) == GPIO.HIGH:
                #If the user pressed the snooze button, go to state 7 and snooze
                if Snooze_Count <= 6:
                    #In state 7, the machine will sleep for 30 min unless release button is pressed or time is up
                    Snooze_Count += 1
                    print('Snooze Button Pressed')
                    os.system('killall -9 mpg123')
                    redisPublisher.publish("This is main","snooze:"+str(6-Snooze_Count))
##                    temp_time = (time.time())//60
##                    cur_time = (time.time())//60
                    temp_time = datetime.datetime.now()
                    cur_time = datetime.datetime.now()
                    while (cur_time - temp_time < snooze_time) and check_expiry(datetime.datetime.now(), current_reg, current_limit) == False: #This while loop handles the case when the machine is snoozing, the snoozing will stop if it reaches 30min of the user pressed the Release Button.
                        cur_time = datetime.datetime.now()
                        if GPIO.input(DISPENSE) == GPIO.HIGH: #If the user pressed the release button,break out of the sleep session
                            break
                    if GPIO.input(DISPENSE) != GPIO.HIGH:
                        os.system("mpg123 http://ice1.somafm.com/u80s-128-mp3 &")
                elif Snooze_Count > 6:
                    non_adherence = 1
                    release = 0


            if non_adherence == 1:
                Snooze_Count = 0
                #If the non adherence flag is turned on,store the medication in the non-adherence storage space
                print('Activate the non-adherence mechanism')
                os.system('killall -9 mpg123')
                nonad_motor.run_forward()
                load_cut.run_dispense()
                time.sleep(1)
                nonad_motor.run_backward()
##                data_logger[str(str(time.asctime()))] = 'not adhere' #store the data logger in the dictionary
                redisPublisher.publish("This is main","Nonad-run") #send the non-adherence data
                non_adherence = 0  #Reset the non adherence flag
                reg = [] #Clear the regimen
                release = 0
                current_reg = datetime.datetime(2099,12, 31)
                redisPublisher.publish("This is main","yes")
##                break

def load_in():
    
    while GPIO.input(PROXIMITY) == GPIO.HIGH:
        if GPIO.input(LOAD) == GPIO.HIGH:
            load_cut.rollforward()
        elif GPIO.input(GET_BACK) == GPIO.HIGH:
            load_cut.rollback()

while True:
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(DISPENSE, GPIO.IN,pull_up_down=GPIO.PUD_DOWN) # defining dispense button
    GPIO.setup(SNOOZE, GPIO.IN,pull_up_down=GPIO.PUD_DOWN) # defining snooze button
    GPIO.setup(TRAVEL, GPIO.IN,pull_up_down=GPIO.PUD_DOWN) # defining travel pack button
    GPIO.setup(PROXIMITY, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # defining proximity sensor
    try:
        load_in()
               
        while GPIO.input(LOAD_COMPLETE) != GPIO.HIGH:
            if GPIO.input(GET_BACK) == GPIO.HIGH:
                load_cut.rollback()
                load_in()
        
        redisPublisher.publish("This is main","Loaded")
        finished = False
        time.sleep(3)
        listen_thread = threading.Thread(target=listen)
        listen_thread.start()
        run()
    except KeyboardInterrupt:
        break
