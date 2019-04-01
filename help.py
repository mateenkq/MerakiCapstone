import time
import datetime
import json

def compare_time(regiment):
    #This function compares the date in medication regiments with the current time, if they are the same, then returns
    #'Y', else returns 'N'.
    time1 = time.localtime()
    year = regiment[0]
    month = regiment[1]
    date = regiment[2]
    hour = regiment[3]
    minute = regiment[4]
    if str(time1.tm_year) == year and str(time1.tm_mon)== month and str(time1.tm_mday) == date and str(time1.tm_hour) == hour and str(time1.tm_min) == minute:
        return 1
    else:
        return 0

def check_expiry(datetime1, datetime2, max_limit):
    if datetime1 - datetime2 >= max_limit:
        return True
    else:
        return False

def validate(year,mon,day,hour,min, time_limit):
    #validate if time is early or late
    past = datetime.date(year,mon,day)
    x = datetime.datetime.now()
    present = datetime.date(x.year,x.month,x.day)
    if past < present:
        #print('early1')
        return 'N'
    elif past > present:
        #print('late2')
        return 'Y'
    else:
        regimen = datetime.datetime(year, mon, day, hour, min, 1, 1)
        if x.time() < regimen.time():
            #print('late1')
            return 'Y'
        else:
            #print('early2')
            if check_expiry(x, regimen, time_limit) is False:
                return 'Y'
            else:
                return 'N'




# Test case for compare_time function
# Y means valid
# N means invalid
# reg_info = ['2019','2','24','20','29']
# x = compare_time(reg_info)
#x= validate(2019,2,24,22,5)
#x = compare_datetime(2019,3,4,14,5)
#print(x)
