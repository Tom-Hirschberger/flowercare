#! /usr/bin/env python3
# install:
#sudo pip3 install miflora
#sudo pip3 install bluepy
#sudo pip3 install paho-mqtt
#sudo pip3 install json5
import sys
import paho.mqtt.client as mqtt
import json5
import pprint
import time
from miflora.miflora_poller import MiFloraPoller
from btlewrap.bluepy import BluepyBackend

def read_json(file_path):
    with open(file_path, "r") as f:
        return json5.load(f)

if len(sys.argv) > 1:
    print("Using config: %s" % sys.argv[1])
    config = read_json(sys.argv[1])
else:
    print("Using config: %s" % "/home/pi/flowercare/config.json")
    config = read_json("/home/pi/flowercare/config.json")

skip = []
pollers = []

client = None

#this function connects the mqtt client to the server
#if a username is specified the credentials will be used
def connect_mqtt_client():
    global client, config
    client = mqtt.Client(config["mqtt"]["clientName"])
    client.connected_flag=False
    client.on_message=callback_on_message
    client.on_disconnect = on_disconnect
    client.on_connect = on_connect
    client.loop_start()
    
    print("Connecting to MQTT broker: %s" % config["mqtt"]["host"])
    try:
        if not ((config["mqtt"]["username"] is None) or (config["mqtt"]["username"] is "")):
            client.username_pw_set(config["mqtt"]["username"], config["mqtt"]["password"])
        client.connect(config["mqtt"]["host"])
    except:
        print("Connection attempt failed!")

    time.sleep(5)
    
    
#this funtion will be called everytime the MQTT connection will be (re-)established
#after the connection is established the client registers to all necessary topics
def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True #set flag
        print("Connected to MQTT broker")
        #client.subscribe(mqtt_topic_prefix+"get_status")
    else:
        print("Bad connection Returned code= ",rc)

#this function is called everytime the MQTT client is disconnected from the server
def on_disconnect(client, userdata, rc):
    print("on_disconnect")
    client.connected_flag = False

#this function is called everytime the MQTT client receives a message
def callback_on_message(client, userdata, message):
    message_str = str(message.payload.decode("utf-8"))
    print ("Received message %s for topic %s" %(message_str, message.topic))


def publish_values(topic,values):
    if client != None and client.connected_flag:
        client.publish(topic,json5.dumps(values))
    else:
        print("Client is not initialized or not connected!")


connect_mqtt_client()

idx = 0
for cur_sensor in config["sensors"]:
    skip.append(0)
    pollers.append(MiFloraPoller(config["sensors"][idx]["mac"], BluepyBackend))
    idx += 1

while True:
    try:
        idx = 0
        for cur_sensor in config["sensors"]:
            if skip[idx] <= 0:
                try:
                    cur_sensor_config = config["sensors"][idx]
                    cur_result = {}
                    if cur_sensor_config["readTemperature"] == True:
                        cur_result["temperature"] = pollers[idx].parameter_value('temperature')
                    if cur_sensor_config["readMoisture"] == True:
                        cur_result["moisture"] = pollers[idx].parameter_value('moisture')
                    if cur_sensor_config["readLight"] == True:
                        cur_result["light"] = pollers[idx].parameter_value('light')
                    if cur_sensor_config["readConductivity"] == True:
                        cur_result["conducitivity"] = pollers[idx].parameter_value('conductivity')
                    if cur_sensor_config["readBattery"] == True: 
                        cur_result["battary"] = pollers[idx].parameter_value('battery')
                        
                    print("Sensor: %s" %cur_sensor_config["name"])
                    pprint.pprint(cur_result, indent=2)
                        
                    publish_values(cur_sensor_config["topic"], cur_result)
                    skip[idx] = cur_sensor_config["interval"] - 1
                except:
                    print("Problems while reading sensor %s. Skipping!" % cur_sensor_config["name"])
                    pass
            else:
                skip[idx] = skip[idx] - 1
            idx += 1
    except:
        pass
    
    time.sleep(config["general"]["sleep"])
