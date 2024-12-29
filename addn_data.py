# create the addn data file here . 
'''
there is supposed to be a one time signal that is sent to the mqtt subscriber at the time of turning off of the vehicle. 
the data to be sent is to be accessed at :  https://chatgpt.com/c/676ed469-c1f0-800f-942b-55b1f7881b36
this would be data that is acclimated and mostly used as a reference.

'''
import json
from flask import Blueprint, Flask, jsonify
import paho.mqtt.client as mqtt
import time

app = Flask(__name__)
file_path = "battery_data.json"
extra_app_bp = Blueprint("addn_info", __name__)  # for final integration only 

status = None

topic = "additional_data"
port = 1883
broker = "localhost"

@app.route('/application/reader', methods=["GET"])
def get_file_contents():
    try:
        global status
        with open(file_path, 'r') as file:
            data = json.load(file)
            status = data.get("AdditionalInfo")
        return status  # for testing only
    except FileNotFoundError as e:
        print(e)
        return "the file is missing bub."

def broadcast_additional_info_updates():
    try:
        global status
        get_file_contents()  # Ensure status is populated before publishing
        mqtt_client = mqtt.Client()
        mqtt_client.connect(broker, port, 60)
        # Assuming 'status' contains the necessary data to be sent
        mqtt_client.publish(topic, json.dumps(status))
        print("Additional data has been sent")  # Send the status as a JSON string
        mqtt_client.disconnect()
    except:
        print("Check out the issue")
        pass
#define a function to send out the socketio signals 


if __name__ == "__main__":
    broadcast_additional_info_updates()
   