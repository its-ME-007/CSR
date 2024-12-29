import paho.mqtt.client as mqtt
import json

broker = "localhost"
port = 1883
topics = ["battery_data","additional_data"]

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        for topic in topics : 
            print("Connected successfully to MQTT broker.")
            client.subscribe(topic)
    else:
        print(f"Connection failed with code {rc}.")

def on_message(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode("utf-8"))
        print(f"Received message on {message.topic}: {payload}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON for topic {message.topic}: {e}")

def subscriber():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    try:
        client.connect(broker, port, 60)
        client.loop_forever()
    except Exception as e:
        print(f"Error connecting to MQTT broker: {e}")

if __name__ == "__main__":
    subscriber()
