import subprocess
import threading
import signal
import time
import os

# List to keep track of subprocesses
subprocesses = []

def run_subscriber():
    """Run the MQTT subscriber."""
    proc = subprocess.Popen(['python', 'subscriber.py'])
    subprocesses.append(proc)

def run_file_reader():
    """Run the file reader."""
    proc = subprocess.Popen(['python', 'file_reader.py'])
    subprocesses.append(proc)

def run_publisher():
    """Run the MQTT publisher."""
    proc = subprocess.Popen(['python', 'publisher.py'])
    subprocesses.append(proc)

def run_addn_data():
    """Run the additional data script once before closing."""
    subprocess.run(['python', 'addn_data.py'])

def run_flask_app():
    """Run the Flask app."""
    proc = subprocess.Popen(['python', 'file_reader.py'])
    subprocesses.append(proc)

def signal_handler(sig, frame):
    """Handle shutdown signals."""
    print("Shutting down file reader, publisher, and Flask app...")
    # Execute addn_data.py before closing
    run_addn_data()
    # Terminate all subprocesses
    for proc in subprocesses:
        proc.terminate()
    print("All subprocesses terminated. Exiting...")
    os._exit(0)  # Forcefully exit all threads and processes

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)  # Register the signal handler

    # Start subprocesses for file reader, publisher, and Flask app
    print("Starting subscriber...")
    subscriber_thread = threading.Thread(target=run_subscriber, daemon=True)
    subscriber_thread.start()

    print("Starting file reader...")
    file_reader_thread = threading.Thread(target=run_file_reader, daemon=True)
    file_reader_thread.start()

    print("Starting publisher...")
    publisher_thread = threading.Thread(target=run_publisher, daemon=True)
    publisher_thread.start()

    print("Starting Flask app...")
    flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    flask_thread.start()

    # Keep the main process alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Keyboard interrupt received. Exiting...")
        signal_handler(None, None)
