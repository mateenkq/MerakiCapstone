#!/usr/bin/env python3

import paho.mqtt.client as mqttClient
import redis
import time
import json
import ast
from datetime import date, datetime, timedelta
from sub_utility import parse_input, output_times

client = None

#Allow time at startup so that network connection is established
##time.sleep(15)


#Set up the redis subscriber to main thru pubsub and set up a redis publisher (redisClient)
redisClient = redis.Redis()
redisSub = redis.Redis()
pubsub = redisSub.pubsub()
pubsub.subscribe("This is main")

#The input dict is initialized with a base structure, and is
#filled as we get data from the Tago platform
input_dict = {'period':'', 'times':[], 'dosages':0}

#TODO --- > If NEW_REGIMEN is True, then input dict will be reinitialized
NEW_REGIMEN = False


result = None
missed = None # the number of meds missed
taken = None # the number of meds taken at the right time

# old data may be stored in onboard memory. See if it's there, if not initialize missed and taken
# to be 0
try:
    fh = open('/home/pi/Dexter/GrovePi/Software/Python/grove_i2c_motor_driver/m8/data.json', 'r')
    data = json.load(fh)
    missed = data['meds_missed']
    taken = data['meds_taken']
    fh.close()
except FileNotFoundError:
    missed = 0
    taken = 0


#Changes need to be made:
  # -Account for the case where result is None -- > should pull data from the
  #  server first then OR display a message "Regimen not uploaded
  # -Account for the edge case where result is length 0          or 1 and so pop will
  #  result in error.

def on_connect(client, userdata, flags, rc):
    """
    Carry out the following tasks when connection to Tago platform
    is established
    
    """
    client.subscribe("tago/test")
    if rc==0:
        print("connected to Tago")
        global Connected
        Connected = True

        # Let the platform know meds are not loaded by updating the remote variable meds_loaded
        send_msg = {
            'variable': "meds_loaded",
            'value': "Meds Have not been loaded yet. Please wait.."
            }
        client.publish("tago/data/post", payload=json.dumps(send_msg))


    else:
        print("Connection Failed")

def on_message(client, userdata, message):
    """
    Carry out the following tasks when a message from the Tago platform is received
    
    """
    global result
    NEW_REGIMEN = True # ---> not doing anything yet, make it useful

    # convert incoming message to a string
    str_recv = ast.literal_eval(message.payload.decode())

    # Change the global variable input_dict based on the information received
    if str(type(input_dict[str_recv["variable"]])) == "<class 'list'>":
        input_dict[str_recv["variable"]].append(str_recv["value"])
    else:

        input_dict[str_recv["variable"]] = str_recv["value"]
    
    """
     A failsafe implemented through some control logic to ensure that the number of dosage times entered
     and the total dosages match. If they don't, pharmacist provided wrong input and needs to provide
     input again. Update pharmacist by updating the remote variable dosages_match
     
    """
    # PROBLEM ---> failsafe only works if the length of the list given by the key 'times' in input_dict
    # is smaller than the number of dosages specified by the key 'dosages' in input dict. This is due
    # to the fact that each time arrives as a separate message and so if the int 'dosages' is less
    # than the actual number of dosage times sent, at some point they'll be both equal within input_dict
    # which will satisfy the conditions of the control logic below. ---> FIX THIS!
    
    if input_dict['period'] != '' and len(input_dict['times']) != 0 and input_dict['dosages'] != 0:
        if len(input_dict['times']) == int(input_dict['dosages']):
            
            start, end, list_of_times = parse_input(input_dict)
            result = output_times(start, end, list_of_times)
            send_msg = {
                'variable': "recv_data",
                'value': "Yes"
            }
            client.publish("tago/data/post", payload=json.dumps(send_msg))


            #reinitialize taken and missed meds

            
            adherence_msg = {
                'variable':'meds_taken',
                'value':taken
                }
            client.publish('tago/data/post', payload=json.dumps(adherence_msg))

            adherence_msg = {
                'variable':'meds_missed',
                'value':missed
                }
            client.publish('tago/data/post', payload=json.dumps(adherence_msg))

            send_msg = {
                'variable': 'dosages_match',
                'value': 'Success!'
            }
            redisClient.publish("wireless", 'new')
            client.publish("tago/data/post", payload=json.dumps(send_msg))

            send_msg = {
                'variable': "meds_loaded",
                'value': "Meds Have not been loaded yet. Please wait.."
            }
            client.publish("tago/data/post", payload=json.dumps(send_msg))

            
        else:
            send_msg = {
                'variable': 'dosages_match',
                'value': 'Please try again!'
            }
            client.publish("tago/data/post", payload=json.dumps(send_msg))
            
    else:
        send_msg = {
            'variable': 'dosages_match',
            'value': 'Please try again!'
        }
        client.publish("tago/data/post", payload=json.dumps(send_msg))


if __name__ == "__main__":
    """
    Set up the MQTT broker and establish a connetion to Tago
    
    """
    Connected = False
    broker_address = "mqtt.tago.io"
    port = 1883
    user="any"
    password="c0664269-298e-45b7-a5c5-5d2af1912363"

    client = mqttClient.Client("Python")
    client.username_pw_set(user, password=password)
    client.on_connect = on_connect
    client.on_message = on_message


    client.connect(broker_address, port=port)
    client.subscribe("tago/test")
    client.loop_start()

    """
    Set up the MQTT broker and establish a connetion to Tago
    
    """

    while True:
        try:
            for item in pubsub.listen():
                if type(item['data']) is not int:
                    item = str(item['data'],'utf-8')
                    if item == 'Loaded':
                        send_msg = {
                            'variable': "meds_loaded",
                            'value': "Meds Have been loaded. Please send regimen to patient."
                        }
                        client.publish("tago/data/post", payload=json.dumps(send_msg))
                    if result == None:
                        redisClient.publish("wireless", 'waiting')
                        continue
                    
                        
                    if item == 'yes' and result is not None:
                        redisClient.publish("wireless", result[0])
                        for item in pubsub.listen():
                            if type(item['data']) is not int:
                                item = str(item['data'], 'utf-8')
                                if item == 'invalid':

                                    missed += 1
                                    result.pop(0)
                                    adherence_msg = {
                                        'variable':'meds_missed',
                                        'value':missed
                                        }
                                    client.publish('tago/data/post', payload=json.dumps(adherence_msg))

                                    local_msg = {
                                        'meds_missed':missed,
                                        'meds_taken':taken
                                        }
                                    with open('/home/pi/Dexter/GrovePi/Software/Python/grove_i2c_motor_driver/m8/data.json', 'w') as outfile:
                                        json.dump(local_msg, outfile)
                                        outfile.close()

                                        
                                    redisClient.publish("wireless", result[0])
                                    continue
                                elif item == 'valid':
                                    break
                        send_msg = {
                            'variable': "recv_data",
                            'value': " "
                        }
                        client.publish("tago/data/post", payload=json.dumps(send_msg))
                           
                    elif item == 'Nonad-run':
                        missed += 1
                        result.pop(0)
                        adherence_msg = {
                            'variable':'meds_missed',
                            'value':missed
                            }
                        client.publish('tago/data/post', payload=json.dumps(adherence_msg))

                        local_msg = {
                            'meds_missed':missed,
                            'meds_taken':taken
                            }
                        with open('/home/pi/Dexter/GrovePi/Software/Python/grove_i2c_motor_driver/m8/data.json', 'w') as outfile:
                            json.dump(local_msg, outfile)
                            outfile.close()
                    elif item == 'Medrun':
                        taken += 1
                        result.pop(0)
                        adherence_msg = {
                            'variable':'meds_taken',
                            'value':taken
                            }
                        client.publish('tago/data/post', payload=json.dumps(adherence_msg))
                        local_msg = {
                            'meds_missed':missed,
                            'meds_taken':taken
                            }
                        with open('/home/pi/Dexter/GrovePi/Software/Python/grove_i2c_motor_driver/m8/data.json', 'w') as outfile:
                            json.dump(local_msg, outfile)
                            outfile.close()
                    
                    elif item == 'no':
                        pass
        except KeyboardInterrupt:
            client.disconnect()
            client.loop_stop()
            break

        while Connected != True:
            time.sleep(0.1)



    print("exiting")
    client.disconnect()
    client.loop_stop()
