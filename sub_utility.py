from datetime import date, datetime, timedelta

def parse_input(input_dict):
    """
    input: input_dict, which is a dictionary containing the input from Tago
           platform in a structured way, with a separate key for the start-end period,
           the dosage times and the total number of dosages each day as entered on
           Tago dashboard

    This function parses the dictionary provided as input and extracts the start and end dates
    as datetime objects, and the list of dosage times as a list.

    returns: start time - a datetime object,
             end time - a datetime object
             times - a list of ints (each int is an hour in 24 hour format)

    """
    start, end = input_dict['period'].split(',')
    start = start.replace('Start:', '').split(' GMT')[0]
    end = end.replace('End:', '').split(' GMT')[0]
    start = datetime.strptime(start, ' %a %b %d %Y %H:%M:%S')
    end = datetime.strptime(end, ' %a %b %d %Y %H:%M:%S')
    times = [int(x) for x in input_dict['times']]
    return start, end, times
    
def output_times(start, end, list_of_times):
    """
    input: start - a datetime object
           end - a datetime object
           list_of_times - a list of hours as ints in the range [0, 23]

    This function takes a start time, an end time, and a list of hours and returns an ordered list
    where each element is a string in a format that can be processed by the controller (see main.py)

    returns: ret_list - a list of strings

    """

    end = end + timedelta(days=1)
    curr_day = start
    ret_list = []
    while curr_day < end:
        for j in list_of_times:
            new_time = curr_day + timedelta(hours=j)
            ret_list.append(new_time)
        curr_day = curr_day + timedelta(days=1)
    ret_list.sort()
    ret_list = [str(x.year)+' '+str(x.month)+' '+str(x.day)+' '+str(x.hour)+' '+str(x.minute) for x in ret_list]
    return ret_list
