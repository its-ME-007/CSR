import subprocess
import time
import signal
import os
import psutil
from flask import Flask, jsonify, request
import threading

# Define Flask App
app = Flask(__name__)

# Define the status dictionary to keep track of the states
status = {
    "Battery": {
        "Voltage": 0,
        "Current": 0,
        "SOC": 0,
        "NumberOfCells": 0,
        "CellVoltage": 0,
        "ChargingMOSFET": "OFF",
        "DischargingMOSFET": "OFF",
        "CellMinimumVoltage": 0,
        "CellMinVoltageNumber": 0,
        "CellMaximumVoltage": 0,
        "CellMaxVoltageNumber": 0,
        "Capacity": 0,
        "ERRORStatus": 0,
        "Temperature": 0
    }
}

# Define Flask routes for battery status
@app.route('/status/battery', methods=['GET'])
def get_battery_status():
    return jsonify(status["Battery"]), 200

@app.route('/battery/<component>/<int:value>', methods=['POST'])
def set_battery_component(component, value):
    if component in status["Battery"]:
        status["Battery"][component] = value
        return jsonify({"status": f"Battery {component} set to {value}"}), 200
    return jsonify({"error": "Invalid component"}), 400

@app.route('/battery/<component>', methods=['GET'])
def get_battery_component(component):
    if component in status["Battery"]:
        return jsonify({component: status["Battery"][component]}), 200
    return jsonify({"error": "Invalid component"}), 400

class ProcessManager:
    def __init__(self):
        self.publisher_process = None
        self.file_reader_process = None
        self.flask_process = None

    def run_publisher(self):
        """Run the MQTT publisher."""
        self.publisher_process = subprocess.Popen(['python', 'publisher.py'])
        return self.publisher_process

    def run_file_reader(self):
        """Run the file reader."""
        self.file_reader_process = subprocess.Popen(['python', 'file_reader.py'])
        return self.file_reader_process

    def run_flask_app(self):
        """Run the Flask app."""
        self.flask_process = subprocess.Popen(['python', 'flask_app.py'])
        return self.flask_process

    def run_addn_data(self):
        """Run the additional data script."""
        print("Running additional data script...")
        try:
            subprocess.run(['python', 'addn_data.py'], check=True)
            print("Additional data script completed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error running addn_data.py: {e}")
            return False

    def kill_process(self, pid):
        """Kill a process and its children."""
        try:
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)
            for child in children:
                child.terminate()
            parent.terminate()
        except psutil.NoSuchProcess:
            pass

    def shutdown(self):
        """Shutdown all processes."""
        print("\nInitiating shutdown...")
        if self.publisher_process:
            print("Terminating publisher...")
            self.kill_process(self.publisher_process.pid)
        if self.file_reader_process:
            print("Terminating file reader...")
            self.kill_process(self.file_reader_process.pid)
        if self.flask_process:
            print("Terminating Flask app...")
            self.kill_process(self.flask_process.pid)
        print("Shutdown complete.")
        os._exit(0)

def main():
    manager = ProcessManager()

    def signal_handler(sig, frame):
        print("\nShutdown signal received...")
        if manager.run_addn_data():  # Run addn_data.py before shutting down
            manager.shutdown()

    signal.signal(signal.SIGINT, signal_handler)

    print("Starting file reader...")
    manager.run_file_reader()

    print("Starting publisher...")
    manager.run_publisher()

    print("Starting Flask app...")
    flask_thread = threading.Thread(target=lambda: app.run(debug=False, use_reloader=False))
    flask_thread.start()

    print("\nSystem is running. Press Ctrl+C to shutdown.")

    try:
        while True:
            time.sleep(1)
    except Exception as e:
        print(f"Error in main loop: {e}")
        manager.shutdown()

if __name__ == "__main__":
    main()
