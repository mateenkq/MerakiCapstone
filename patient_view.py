#!/usr/bin/env python3

import RPi.GPIO as GPIO
from tkinter import *
import threading
import tkinter.font
import redis
import time
import datetime
import sys


MEDS_NOW = 0
TRAVEL_MODE = 0
SNOOZE = 0
snooze_count = 0
travel_count = 0


redisClient = redis.Redis()
redisSub = redis.Redis()
pubsub = redisSub.pubsub()
pubsub.subscribe("This is main")
press = 0
            

def Dispense():
    pass

def Snooze():
    pass

def Travel():
    pass


class MyApp(threading.Thread):
    def __init__(self, next_lab, top, med, low):
        self.next_lab = next_lab
        self.top = top
        self.med = med
        self.low = low
        threading.Thread.__init__(self)


    def check_main(self):
        reg = ""
        for item in pubsub.listen():
            if type(item['data']) is not int:
                item = str(item['data'], 'utf-8')
                if item == 'Loaded':
                    self.top.config(text='Dispense')
                    self.med.config(text='Snooze')
                    self.low.config(text='Travel Pk')
                    self.next_lab.config(text='Please Wait for Pharmacist')
                elif item[:4] == 'next':
                    self.top.config(text='Dispense')
                    self.med.config(text='Snooze')
                    self.low.config(text='Travel Pk')
                    reg = item[6:].split()
                    reg = datetime.datetime(*[int(i) for i in reg[:5]])
                    reg = reg.ctime()
##                    reg = reg.strftime("Next Dosage: %H:%M:%S")
                    self.next_lab.config(text='Next Dosage:\n'+str(reg))
                elif item == 'discarding':
                    self.top.config(text='Dispense')
                    self.med.config(text='Snooze')
                    self.low.config(text='Travel Pk')
                    self.next_lab.config(text='Discarding old meds...')
                    time.sleep(3)
                    self.next_lab.config(text=reg)
                    
                elif item == 'can_dispense':
                    self.top.config(text='Dispense')
                    self.med.config(text='Snooze')
                    self.low.config(text='Travel Pk')
                    self.next_lab.config(text='Please take your meds!')
                elif item == 'dispensing':
                    self.top.config(text='Dispense')
                    self.med.config(text='Snooze')
                    self.low.config(text='Travel Pk')
                    self.next_lab.config(text='Dispensing...')
                elif item == 'dispense-travel':
                    self.next_lab.config(text='Travel Pack...')
                elif item.split(':')[0] == 'snooze':
                    self.next_lab.config(text='Snoozes Left: '+item.split(':')[1])
                elif item == 'finished':
                    self.top.config(text='Reset')
                    self.med.config(text='')
                    self.low.config(text='Load In')
                    self.next_lab.config(text='Old regimen finished!\nLoad New!')
                elif item == 'Load-Confirmation':
                    self.top.config(text='No(Reset)')
                    self.med.config(text='')
                    self.low.config(text='Yes')
                    self.next_lab.config(text='New meds detected. Proceed?')
            else:
                print('a')
                continue

    def run(self):
        while True:
            try:
                self.check_main()
            except KeyboardInterrupt:
                break


def main():    
    root = Tk()
    helv36 = tkinter.font.Font(family='Helvetica', size=70, weight='bold')
    root.attributes('-fullscreen', True)
    guistr = StringVar()
    x1 = Label(root, textvariable=guistr)
    x1.config(font=('Helvetica',20,'bold'))


    top = Button(root, text='Reset', font = helv36, command=Dispense)
    top.pack(side=TOP, anchor=W)
    med = Button(root, text='', font = helv36, command=Snooze)
    med.place(relx=0.0, rely=0.5, anchor=NW)
    low = Button(root, text='Load In', font = helv36, command=Travel)
    low.pack(side=BOTTOM, anchor=W)

    
    time_lab = Label(root,
                text = datetime.datetime.now().strftime("Time: %H:%M:%S"),
                fg = 'blue',
                bg = 'yellow',
                font = "Helvetica 40 underline")
    time_lab.place(relx=1, rely=0.1, anchor=E)
##    lab.pack()

    next_lab = Label(root,
                     text = 'Please Load In Medication',
                     fg = 'yellow',
                     bg = 'red',
                     font = "Helvetica 40 bold")
    
    next_lab.place(relx=1, rely=0.6, anchor=E)

    def clock():
        time = datetime.datetime.now().strftime("Time: %H:%M:%S")
        time_lab.config(text=time)
        root.after(1000, clock)
    clock()


                
    while True:
        try:
            app = MyApp(next_lab, top, med, low)
            app.start()
            root.mainloop()
        except KeyboardInterrupt:
            break
        

if __name__ == '__main__':
    main()
