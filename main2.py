import subprocess
import time
import signal
import os
import threading
import psutil
import sys
from queue import Queue, Empty  # Import Empty exception specifically

class ProcessManager:
    def __init__(self):
        self.processes = {}
        self.shutdown_flag = threading.Event()
        self.completion_queue = Queue()

    def run_subscriber(self):
        """Run the MQTT subscriber."""
        process = subprocess.Popen(['python', 'subscriber.py'])
        self.processes['subscriber'] = process
        return process

    def run_file_reader(self):
        """Run the file reader."""
        process = subprocess.Popen(['python', 'file_reader.py'])
        self.processes['file_reader'] = process
        return process

    def run_publisher(self):
        """Run the MQTT publisher."""
        process = subprocess.Popen(['python', 'publisher.py'])
        self.processes['publisher'] = process
        return process

    def run_addn_data(self):
        """Run the additional data script and wait for completion."""
        try:
            print("Running additional data script...")
            result = subprocess.run(['python', 'addn_data.py'], check=True)
            self.completion_queue.put(('addn_data', result.returncode))
        except subprocess.CalledProcessError as e:
            print(f"Error running addn_data.py: {e}")
            self.completion_queue.put(('addn_data', e.returncode))

    def run_flask_app(self):
        """Run the Flask app."""
        from file_reader import app
        app.run(debug=False, use_reloader=False, port=5007)

    def kill_process_tree(self, pid):
        """Kill a process and all its children."""
        try:
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)
            for child in children:
                child.terminate()
            parent.terminate()
        except psutil.NoSuchProcess:
            pass

    def shutdown(self):
        """Gracefully shutdown all processes."""
        print("\nInitiating shutdown sequence...")
        
        # Set shutdown flag
        self.shutdown_flag.set()
        
        # Kill all processes
        for name, process in self.processes.items():
            print(f"Terminating {name}...")
            self.kill_process_tree(process.pid)
        
        # Kill Flask app if running
        current_process = psutil.Process()
        children = current_process.children(recursive=True)
        for child in children:
            try:
                child.terminate()
            except psutil.NoSuchProcess:
                pass

        print("Shutdown complete.")
        os._exit(0)  # Use os._exit instead of sys.exit

def main():
    manager = ProcessManager()

    def signal_handler(sig, frame):
        manager.shutdown()

    signal.signal(signal.SIGINT, signal_handler)

    # Start subscriber
    print("Starting subscriber...")
    manager.run_subscriber()
    time.sleep(1)  # Wait for subscriber to initialize

    # Start file reader and publisher
    print("Starting file reader and publisher...")
    manager.run_file_reader()
    manager.run_publisher()

    # Start Flask app in a separate thread
    flask_thread = threading.Thread(target=manager.run_flask_app)
    flask_thread.daemon = True  # Make thread daemon so it exits when main program exits
    flask_thread.start()

    # Start addn_data monitoring thread
    addn_data_thread = threading.Thread(target=manager.run_addn_data)
    addn_data_thread.start()

    # Wait for addn_data to complete
    try:
        while True:
            try:
                task, return_code = manager.completion_queue.get(timeout=1)
                if task == 'addn_data':
                    print("Additional data script completed.")
                    manager.shutdown()
                    break
            except Empty:  # Changed from Queue.Empty to Empty
                continue
    except KeyboardInterrupt:
        manager.shutdown()

if __name__ == "__main__":
    main()