import paho.mqtt.client as mqtt
import json
import pandas as pd
import os

broker = "localhost"
port = 1883
topics = ["battery_data", "additional_data"]

# File paths for CSVs
battery_csv = "battery_data.csv"
additional_csv = "additional_data.csv"

# Initialize CSV files if they don't exist
if not os.path.exists(battery_csv):
    pd.DataFrame().to_csv(battery_csv, index=False)
if not os.path.exists(additional_csv):
    pd.DataFrame().to_csv(additional_csv, index=False)

def save_to_csv(data, topic):
    """Append new data to the appropriate CSV file."""
    df = pd.DataFrame([data])
    if topic == "battery_data":
        csv_file = battery_csv
    elif topic == "additional_data":
        csv_file = additional_csv
    else:
        return

    # Append to the CSV
    if os.path.exists(csv_file):
        df.to_csv(csv_file, mode="a", header=False, index=False)
    else:
        df.to_csv(csv_file, index=False)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        for topic in topics:
            print("Connected successfully to MQTT broker.")
            client.subscribe(topic)
    else:
        print(f"Connection failed with code {rc}.")

def on_message(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode("utf-8"))
        print(f"Received message on {message.topic}: {payload}")

        # Save received data to CSV
        save_to_csv(payload, message.topic)

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
