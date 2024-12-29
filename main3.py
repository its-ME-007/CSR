import subprocess
import time
import signal
import os
import psutil
from queue import Queue

class ProcessManager:
    def __init__(self):
        self.publisher_process = None

    def run_publisher(self):
        """Run the MQTT publisher."""
        self.publisher_process = subprocess.Popen(['python', 'publisher.py'])
        return self.publisher_process

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
        """Shutdown the publisher process."""
        print("\nInitiating publisher shutdown...")
        if self.publisher_process:
            print("Terminating publisher...")
            self.kill_process(self.publisher_process.pid)
        print("Shutdown complete.")
        os._exit(0)

def main():
    manager = ProcessManager()

    def signal_handler(sig, frame):
        print("\nShutdown signal received...")
        if manager.run_addn_data():  # Run addn_data.py before shutting down
            manager.shutdown()

    signal.signal(signal.SIGINT, signal_handler)

    # Start publisher
    print("Starting publisher...")
    manager.run_publisher()

    print("\nSystem is running. Press Ctrl+C to shutdown.")
    
    try:
        while True:
            time.sleep(1)
    except Exception as e:
        print(f"Error in main loop: {e}")
        manager.shutdown()

if __name__ == "__main__":
    main()