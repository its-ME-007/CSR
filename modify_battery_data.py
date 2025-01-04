from flask import Blueprint
import json
import time
import random
from datetime import datetime

# Create a blueprint for modify_battery_data
modify_battery_data_bp = Blueprint('modify_battery_data', __name__)

STATUS_FILE_PATH = 'battery_data.json'

battery_data = {
    "Battery": {
        "Voltage_1": 4.07,
        "Voltage_2": 1,
        "Voltage_3": 2,
        "Voltage_4": 2.5,
        "Voltage_5": 2.5,
        "Voltage_6": 2.5,
        "Voltage_7": 2.5,
        "Voltage_8": 2.5,
        "Voltage_9": 2.5,
        "Voltage_10": 2.5,
        "Voltage_11": 2.5,
        "Voltage_12": 2.5,
        "Voltage_13": 2.5,
        "Voltage_14": 2.5,
        "Voltage_15": 2.5,
        "Voltage_16": 2.5,
        "Voltage_17": 2.5,
        "Voltage_18": 2.5,
        "Voltage_19": 2.5,
        "Voltage_20": 2.5,
        "Voltage_21": 2.5,
        "Voltage_22": 2.5,
        "Voltage_23": 2.5,
        "Voltage_24": 2.5,
        "Current": 4.3,
        "SOC": 85,
        "NumberOfCells": 24,
        "CellVoltage": 50.4,
        "ChargingMOSFET": "ON",
        "DischargingMOSFET": "ON",
        "CellMinimumVoltage": 2.1,
        "CellMaximumVoltage": 2.2,
        "Capacity": 55,
        "ERRORStatus": 0,
        "Temperature": 35
    },
    "AdditionalInfo": {
        "DistanceTravelled": 0,
        "Runtime": 0,
        "RangeLeft": 10000,
        "Date": ""
    }
}

def save_battery_status():
    """Save the battery data to the JSON file."""
    with open(STATUS_FILE_PATH, 'w') as file:
        json.dump(battery_data, file, indent=4)

@modify_battery_data_bp.route('/publish', methods=['POST'])
def publish_battery_data():
    while True:
        battery_data["Battery"]["Voltage_7"] = round(random.uniform(2.0, 4.2), 2) 
        
        battery_data["Battery"]["Current"] = random.uniform(0, 10)  
        battery_data["Battery"]["SOC"] = random.randint(20, 100) 
        battery_data["Battery"]["CellVoltage"] = sum(battery_data["Battery"][f"Voltage_{i}"] for i in range(1, 25))  
        
        battery_data["Battery"]["CellMinimumVoltage"] = min(battery_data["Battery"][f"Voltage_{i}"] for i in range(1, 25))
        battery_data["Battery"]["CellMaximumVoltage"] = max(battery_data["Battery"][f"Voltage_{i}"] for i in range(1, 25))

        battery_data["AdditionalInfo"]["DistanceTravelled"] += random.uniform(0.1, 1.0)
        battery_data["AdditionalInfo"]["Runtime"] += 1
        battery_data["AdditionalInfo"]["RangeLeft"] -= random.uniform(0.1, 0.5)

        battery_data["AdditionalInfo"]["RangeLeft"] = max(battery_data["AdditionalInfo"]["RangeLeft"], 0)

        battery_data["AdditionalInfo"]["Date"] = datetime.now().strftime("%Y-%m-%d")
        save_battery_status()

        time.sleep(0.7)

if __name__ == "__main__":
    publish_battery_data()
