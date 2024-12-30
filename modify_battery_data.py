import json
import time
import random
from datetime import datetime

STATUS_FILE_PATH = 'battery_data.json'

# Sample battery data
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
        "Voltage_24": 2.5,  # Initialize with 24 cells 
        "Current": 4.3,
        "SOC": 85,
        "NumberOfCells": 24,
        "CellVoltage": 50.4,  # Example total voltage for 24 cells
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
        "RangeLeft": 10000,  # Assuming a starting range
        "Date": ""
    }
}

def save_battery_status():
    """Save the battery data to the JSON file."""
    with open(STATUS_FILE_PATH, 'w') as file:
        json.dump(battery_data, file, indent=4)

def publish_battery_data():
    while True:
        # Simulate real-time updates to battery status
        # Randomly vary the voltage of one of the cells
        battery_data["Battery"]["Voltage_7"] = round(random.uniform(2.0, 4.2), 2)  # Fixed indexing
        
        # Update other battery attributes randomly
        battery_data["Battery"]["Current"] = random.uniform(0, 10)  # Random current between 0 and 10
        battery_data["Battery"]["SOC"] = random.randint(20, 100)  # Random SOC between 20 and 100
        battery_data["Battery"]["CellVoltage"] = sum(battery_data["Battery"][f"Voltage_{i}"] for i in range(1, 25))  # Update total cell voltage
        
        # Update minimum and maximum voltage based on the current voltage list
        battery_data["Battery"]["CellMinimumVoltage"] = min(battery_data["Battery"][f"Voltage_{i}"] for i in range(1, 25))  # Fixed calculation
        battery_data["Battery"]["CellMaximumVoltage"] = max(battery_data["Battery"][f"Voltage_{i}"] for i in range(1, 25))  # Fixed calculation

        # Update additional info values
        battery_data["AdditionalInfo"]["DistanceTravelled"] += random.uniform(0.1, 1.0)  # Increase distance travelled randomly
        battery_data["AdditionalInfo"]["Runtime"] += 1  # Increase runtime linearly
        battery_data["AdditionalInfo"]["RangeLeft"] -= random.uniform(0.1, 0.5)  # Decrease range left randomly

        # Ensure range_left does not go below zero
        battery_data["AdditionalInfo"]["RangeLeft"] = max(battery_data["AdditionalInfo"]["RangeLeft"], 0)

        # Update the date to the current date
        battery_data["AdditionalInfo"]["Date"] = datetime.now().strftime("%Y-%m-%d")  # Set current date

        save_battery_status()  # Save to the JSON file

        time.sleep(0.7)  # Publish interval, can be modified as per our requirement

if __name__ == "__main__":
    publish_battery_data()