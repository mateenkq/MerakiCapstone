import os
import time
os.system("mpg123 http://ice1.somafm.com/u80s-128-mp3 &")
time.sleep(5)
os.system('killall -9 mpg123')
