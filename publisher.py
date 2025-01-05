import paho.mqtt.client as mqtt
import json
import time
from flask import Blueprint

broker = "localhost"
port = 1883
topic = "battery_data"

publisher = Blueprint("publisher",__name__)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully to MQTT broker.")
    else:
        print(f"Connection failed with code {rc}.")

def publish_data():
    client = mqtt.Client()
    client.on_connect = on_connect
    
    try:
        client.connect(broker, port, 60)
        client.loop_start()
        
        while True:
            try:
                with open("battery_data.json", 'r') as file:
                    data = json.load(file)
                    payload = data.get("Battery",{})
                    client.publish(topic, json.dumps(payload), retain=False)
                    print(f"Published to {topic}")
            except Exception as e:
                print(f"Error reading or publishing data: {e}")
                
            time.sleep(3) 
             # Adjusted for 5 minutes
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    publish_data()
