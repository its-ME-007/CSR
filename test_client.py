from flask import Flask
from flask_socketio import SocketIO
import socketio

# Create a SocketIO client
sio = socketio.Client()

# Event handler for receiving battery updates
@sio.on('voltage_1')  # Change this to the specific event you want to test
def handle_voltage_1(data):
    print(f"Received Voltage 1 update: {data}")

@sio.on('current')  # Listening for current updates
def handle_current(data):
    print(f"Received Current update: {data}")

@sio.on('soc')  # Listening for SOC updates
def handle_soc(data):
    print(f"Received SOC update: {data}")

@sio.on('cell_minimum_voltage')  # Listening for CellMinimumVoltage updates
def handle_cell_minimum_voltage(data):
    print(f"Received Cell Minimum Voltage update: {data}")

@sio.on('cell_maximum_voltage')  # Listening for CellMaximumVoltage updates
def handle_cell_maximum_voltage(data):
    print(f"Received Cell Maximum Voltage update: {data}")

@sio.on('error')  # Listening for error messages
def handle_error(data):
    print(f"Received error: {data}")

if __name__ == "__main__":
    # Connect to the SocketIO server
    sio.connect('http://localhost:5000')  # Adjust the port if necessary
    sio.wait()  # Wait for events 