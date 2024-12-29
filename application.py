from flask_socketio import SocketIO, emit
from flask import Blueprint, Flask
import paho.mqtt.client as mqtt
import json
import time
from copy import deepcopy

# Configuration
VALID_RANGES = {
    "cell_voltage": (0, 5),
    "soc": (20, 100),
    "current": (0, 100),
    "cell_minimum_voltage": (0, 5),
    "cell_maximum_voltage": (0, 10)
}

MQTT_CONFIG = {
    "broker": "localhost",
    "port": 1883,
    "topic": "battery_data",
    "keepalive": 60
}

FILE_PATH = "battery_data.json"

app = Blueprint("application", __name__)
socketio = SocketIO()

class BatteryMonitor:
    def __init__(self):
        self.current_status = None
        self.last_status = None
        self.mqtt_client = None

    def get_file_contents(self):
        try:
            with open(FILE_PATH, 'r') as file:
                self.current_status = json.load(file)
                return True
        except FileNotFoundError:
            print(f"File not found: {FILE_PATH}")
            return False
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return False

    def validate_data(self):
        if not self.current_status or "Battery" not in self.current_status:
            return False, "Invalid data structure", 400

        battery_data = self.current_status["Battery"]
        
        soc = battery_data.get("SOC", 0)
        if not (VALID_RANGES["soc"][0] <= soc <= VALID_RANGES["soc"][1]):
            return False, f"SOC value {soc} outside valid range {VALID_RANGES['soc']}", 400

        for i in range(1, 25):
            voltage_key = f"Voltage_{i}"
            voltage = battery_data.get(voltage_key, 0)
            if not (VALID_RANGES["cell_voltage"][0] <= voltage <= VALID_RANGES["cell_voltage"][1]):
                return False, f"{voltage_key} value {voltage} outside valid range {VALID_RANGES['cell_voltage']}", 400

        return True, "Battery validation successful", 200

    def broadcast_updates(self):
        while True:
            if not self.get_file_contents():
                socketio.sleep(1)
                continue

            is_valid, msg, status = self.validate_data()
            if not is_valid:
                socketio.emit('error', {'message': msg})
                socketio.sleep(1)
                continue

            if self.current_status != self.last_status:
                battery_data = self.current_status["Battery"]
                
                self._emit_voltage_updates(battery_data)
                self._emit_metric_update(battery_data, 'Current', 'current', VALID_RANGES['current'])
                self._emit_metric_update(battery_data, 'SOC', 'soc', VALID_RANGES['soc'])
                self._emit_metric_update(
                    battery_data,
                    'CellMinimumVoltage',
                    'cell_minimum_voltage',
                    VALID_RANGES['cell_minimum_voltage']
                )
                self._emit_metric_update(
                    battery_data,
                    'CellMaximumVoltage',
                    'cell_maximum_voltage',
                    VALID_RANGES['cell_maximum_voltage']
                )

                self.last_status = deepcopy(self.current_status)
                #self.publish_updates()

            socketio.sleep(0.7)

    def _emit_voltage_updates(self, battery_data):
        for i in range(1, 25):
            voltage_key = f"Voltage_{i}"
            if voltage_key in battery_data:
                voltage_value = battery_data[voltage_key]
                if not self.last_status or voltage_value != self.last_status["Battery"].get(voltage_key):
                    if VALID_RANGES["cell_voltage"][0] <= voltage_value <= VALID_RANGES["cell_voltage"][1]:
                        socketio.emit(voltage_key.lower(), {voltage_key: voltage_value})
                    else:
                        socketio.emit('error', {
                            voltage_key: f"{voltage_key} value {voltage_value} out of range {VALID_RANGES['cell_voltage']}"
                        })

    def _emit_metric_update(self, battery_data, metric_key, event_name, valid_range):
        value = battery_data.get(metric_key)
        if value is not None and (
            not self.last_status or 
            value != self.last_status["Battery"].get(metric_key)
        ):
            if valid_range[0] <= value <= valid_range[1]:
                socketio.emit(event_name, {metric_key: value})
            else:
                socketio.emit('error', {
                    metric_key: f"{metric_key} value {value} out of range {valid_range}"
                })

@app.route('/battery/status')
def get_battery_status():
    monitor = BatteryMonitor()
    if monitor.get_file_contents():
        is_valid, msg, status = monitor.validate_data()
        if is_valid:
            return monitor.current_status, 200
        return {"error": msg}, status
    return {"error": "Failed to read battery data"}, 400

def init_monitoring():
    monitor = BatteryMonitor()
    if monitor.setup_mqtt():
        socketio.start_background_task(monitor.broadcast_updates)
    else:
        print("Failed to initialize monitoring system")