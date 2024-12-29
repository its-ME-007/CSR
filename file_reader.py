from flask_socketio import SocketIO,emit
import json
from flask import Blueprint,Flask,jsonify
import paho.mqtt.client as mqtt

valid_ranges = {
        "cell_voltage": (0,5),  # Standard Li-ion cell voltage range
        "soc": (20, 100),  # From valid_ranges
}
app = Flask(__name__)
file_path = "battery_data.json"
appbp = Blueprint("application",__name__) #for final integration only 
socketio = SocketIO(app)
current_status = None
last_status = None

topic = "battery_data"
port = 1883
broker = "localhost"

@app.route('/application/reader',methods = ["GET"])
def get_file_contents():
    try:
        global current_status
        with open(file_path, 'r') as file:
            data= json.load(file)
            current_status = data.get("Battery")
        return current_status #for testing only
    except FileNotFoundError as e :
        print(e)
        return "the file is missing bub." 
    
# app.route('application/validate')
def validater():
    soc = current_status.get("SOC", 0)
    if not (valid_ranges["soc"][0] <= soc <= valid_ranges["soc"][1]):
        msg = f"SOC value {soc} outside valid range {valid_ranges['soc']}"
        #logging.warning(msg)
        return False, msg, 400
    
    for i in range(1, 25):
        voltage_key = f"Voltage_{i}"
        voltage = current_status.get(voltage_key, 0)
        if not (valid_ranges["cell_voltage"][0] <= voltage <= valid_ranges["cell_voltage"][1]):
            msg = f"{voltage_key} value {voltage} outside valid range {valid_ranges['cell_voltage']}"
            #logging.warning(msg)
            return False, msg, 400
        
    return True, "Battery validation successful", 200

@app.route('/application/sockets')
def broadcast_battery_updates():
    """Emit updates only when there are status changes for each battery component."""
    global last_status
    while True:
        get_file_contents()
        if current_status != last_status:
            battery_data = current_status["Battery"]

            # Validate before emitting
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
            last_status = current_status.copy()

        socketio.sleep(0.7)

if __name__ == "__main__":
    #app.run(debug = True)
    socketio.run(app)