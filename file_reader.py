from flask import Blueprint, Flask, jsonify, render_template
from flask_socketio import SocketIO, emit
import json
import logging
import threading 

valid_ranges = {
        "cell_voltage": (0,5),  # Standard Li-ion cell voltage range
        "soc": (20, 100),  # From valid_ranges
}
file_path = "battery_data.json"
# Create a blueprint for file_reader
file_reader_bp = Blueprint('file_reader', __name__)
socketio = SocketIO(cors_allowed_origins="http://127.0.0.1:5000")
battery_data = None
last_status = None

topic = "battery_data"
port = 1883
broker = "localhost"

@file_reader_bp.route('/')
def index():
    """Serve the HTML template for testing SocketIO connections."""
    return render_template('template.html')  # Serve the HTML file

@file_reader_bp.route('/application/reader', methods=["GET"])
def get_file_contents():
    try:
        global battery_data
        with open(file_path, 'r') as file:
            battery_data = json.load(file)
            battery_data = battery_data.get("Battery")
        return battery_data  # for testing only
    except FileNotFoundError as e:
        print(e)
        return "the file is missing bub." 

# app.route('application/validate')
def validater():
    soc = battery_data.get("SOC", 0)
    if not (valid_ranges["soc"][0] <= soc <= valid_ranges["soc"][1]):
        msg = f"SOC value {soc} outside valid range {valid_ranges['soc']}"
        logging.warning(msg)
        return False, msg, 400
    
    for i in range(1, 25):
        voltage_key = f"Voltage_{i}"
        voltage = battery_data.get(voltage_key, 0)
        if not (valid_ranges["cell_voltage"][0] <= voltage <= valid_ranges["cell_voltage"][1]):
            msg = f"{voltage_key} value {voltage} outside valid range {valid_ranges['cell_voltage']}"
            logging.warning(msg)
            return False, msg, 400
        
    return True, "Battery validation successful", 200

def broadcast_battery_updates():
    """Emit updates only when there are status changes for each battery component."""
    global last_status
    while True:
        get_file_contents()
        if battery_data != last_status:
            # Validate before emitting
            last_status = battery_data.copy()
            is_valid, validation_msg, status_code = validater()
            if not is_valid:
                print(validation_msg)  # Log or handle the validation error
                continue  # Skip emitting if validation fails

            # Validate and emit updates for battery status
            '''for i in range(1, 25):
                voltage_key = f"Voltage_{i}"
                voltage_value = battery_data[voltage_key]
                if voltage_value != last_status["Battery"].get(voltage_key, None):
                    if not (valid_ranges["cell_voltage"][0] <= voltage_value <= valid_ranges["cell_voltage"][1]):
                        socketio.emit('error', {voltage_key: f"{voltage_key} value {voltage_value} out of range {valid_ranges['cell_voltage']}"}, broadcast=True)
                    else:
                        socketio.emit(voltage_key.lower(), {voltage_key: voltage_value}, broadcast=True)'''

            # Validate and emit Current
            current_value = battery_data["Current"]
            if current_value != last_status["Battery"].get("Current", None):
                if not (0 <= current_value <= 100):  
                    socketio.emit('error', {"Current": f"Current value {current_value} out of range [0, 100]"}, broadcast=True)
                else:
                    socketio.emit('current', {"Current": current_value}, broadcast=True)

            # Validate and emit SOC
            soc_value = battery_data["SOC"]
            if soc_value != last_status["Battery"].get("SOC", None):
                if not (valid_ranges["soc"][0] <= soc_value <= valid_ranges["soc"][1]):
                    socketio.emit('error', {"SOC": f"SOC value {soc_value} out of range {valid_ranges['soc']}"}, broadcast=True)
                else:
                    socketio.emit('soc', {"SOC": soc_value}, broadcast=True)

            # Validate and emit CellMinimumVoltage
            min_voltage_value = battery_data["CellMinimumVoltage"]
            if min_voltage_value != last_status["Battery"].get("CellMinimumVoltage", None):
                if not (0 <= min_voltage_value <= 5):  # Assuming a valid range for CellMinimumVoltage
                    socketio.emit('error', {"CellMinimumVoltage": f"CellMinimumVoltage value {min_voltage_value} out of range [0, 5]"}, broadcast=True)
                else:
                    socketio.emit('cell_minimum_voltage', {"CellMinimumVoltage": min_voltage_value}, broadcast=True)

            # Validate and emit CellMaximumVoltage
            max_voltage_value = battery_data["CellMaximumVoltage"]
            if max_voltage_value != last_status["Battery"].get("CellMaximumVoltage", None):
                if not (5 <= max_voltage_value <= 10):  # Assuming a valid range for CellMaximumVoltage
                    socketio.emit('error', {"CellMaximumVoltage": f"CellMaximumVoltage value {max_voltage_value} out of range [0, 5]"}, broadcast=True)
                else:
                    socketio.emit('cell_maximum_voltage', {"CellMaximumVoltage": max_voltage_value}, broadcast=True)

        socketio.sleep(0.7)

# Start the broadcast thread
update_thread = threading.Thread(target=broadcast_battery_updates)
update_thread.daemon = True
update_thread.start()
import json
from flask import Blueprint,Flask,jsonify,render_template
import paho.mqtt.client as mqtt
import logging
import threading 

valid_ranges = {
        "cell_voltage": (0,5),  # Standard Li-ion cell voltage range
        "soc": (20, 100),  # From valid_ranges
}
app = Flask(__name__)
file_path = "battery_data.json"
 
socketio = SocketIO(app, cors_allowed_origins="http://127.0.0.1:5000")
battery_data = None
last_status = None

topic = "battery_data"
port = 1883
broker = "localhost"

@app.route('/')
def index():
    """Serve the HTML template for testing SocketIO connections."""
    return render_template('template.html')  # Serve the HTML file

@app.route('/application/reader',methods = ["GET"])
def get_file_contents():
    try:
        
        global battery_data
        with open(file_path, 'r') as file:
            battery_data= json.load(file)
            battery_data = battery_data.get("Battery")
        return battery_data #for testing only
    except FileNotFoundError as e :
        print(e)
        return "the file is missing bub." 
    
# app.route('application/validate')
def validater():
    soc = battery_data.get("SOC", 0)
    if not (valid_ranges["soc"][0] <= soc <= valid_ranges["soc"][1]):
        msg = f"SOC value {soc} outside valid range {valid_ranges['soc']}"
        logging.warning(msg)
        return False, msg, 400
    
    for i in range(1, 25):
        voltage_key = f"Voltage_{i}"
        voltage = battery_data.get(voltage_key, 0)
        if not (valid_ranges["cell_voltage"][0] <= voltage <= valid_ranges["cell_voltage"][1]):
            msg = f"{voltage_key} value {voltage} outside valid range {valid_ranges['cell_voltage']}"
            logging.warning(msg)
            return False, msg, 400
        
    return True, "Battery validation successful", 200

def broadcast_battery_updates():
    """Emit updates only when there are status changes for each battery component."""
    global last_status
    while True:
        get_file_contents()
        if battery_data != last_status:
            # Validate before emitting
            last_status = battery_data.copy()
            is_valid, validation_msg, status_code = validater()
            if not is_valid:
                print(validation_msg)  # Log or handle the validation error
                continue  # Skip emitting if validation fails

            # Validate and emit updates for battery status
            for i in range(1, 25):
                voltage_key = f"Voltage_{i}"
                voltage_value = battery_data[voltage_key]
                if voltage_value != last_status["Battery"].get(voltage_key, None):
                    if not (valid_ranges["cell_voltage"][0] <= voltage_value <= valid_ranges["cell_voltage"][1]):
                        socketio.emit('error', {voltage_key: f"{voltage_key} value {voltage_value} out of range {valid_ranges['cell_voltage']}"}, broadcast=True)
                    else:
                        socketio.emit(voltage_key.lower(), {voltage_key: voltage_value}, broadcast=True)

            # Validate and emit Current
            current_value = battery_data["Current"]
            if current_value != last_status["Battery"].get("Current", None):
                if not (0 <= current_value <= 100):  
                    socketio.emit('error', {"Current": f"Current value {current_value} out of range [0, 100]"}, broadcast=True)
                else:
                    socketio.emit('current', {"Current": current_value}, broadcast=True)

            # Validate and emit SOC
            soc_value = battery_data["SOC"]
            if soc_value != last_status["Battery"].get("SOC", None):
                if not (valid_ranges["soc"][0] <= soc_value <= valid_ranges["soc"][1]):
                    socketio.emit('error', {"SOC": f"SOC value {soc_value} out of range {valid_ranges['soc']}"}, broadcast=True)
                else:
                    socketio.emit('soc', {"SOC": soc_value}, broadcast=True)

            # Validate and emit CellMinimumVoltage
            min_voltage_value = battery_data["CellMinimumVoltage"]
            if min_voltage_value != last_status["Battery"].get("CellMinimumVoltage", None):
                if not (0 <= min_voltage_value <= 5):  # Assuming a valid range for CellMinimumVoltage
                    socketio.emit('error', {"CellMinimumVoltage": f"CellMinimumVoltage value {min_voltage_value} out of range [0, 5]"}, broadcast=True)
                else:
                    socketio.emit('cell_minimum_voltage', {"CellMinimumVoltage": min_voltage_value}, broadcast=True)

            # Validate and emit CellMaximumVoltage
            max_voltage_value = battery_data["CellMaximumVoltage"]
            if max_voltage_value != last_status["Battery"].get("CellMaximumVoltage", None):
                if not (5 <= max_voltage_value <= 10):  # Assuming a valid range for CellMaximumVoltage
                    socketio.emit('error', {"CellMaximumVoltage": f"CellMaximumVoltage value {max_voltage_value} out of range [0, 5]"}, broadcast=True)
                else:
                    socketio.emit('cell_maximum_voltage', {"CellMaximumVoltage": max_voltage_value}, broadcast=True)
            # Update the last_status to the current one
           

        socketio.sleep(0.7)

if __name__ == "__main__":
    
    
    update_thread = threading.Thread(target=broadcast_battery_updates)

    update_thread.daemon = True
    update_thread.start()
    socketio.run(app)