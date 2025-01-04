import json
from threading import Thread
from addn_data import broadcast_additional_info_updates
from modify_battery_data import publish_battery_data
from publisher import publish_data

def start_battery_data_publishing():
    publish_battery_data()

def start_publishing():
    publish_data()

if __name__ == "__main__":
    # Start the battery data publishing thread
    battery_thread = Thread(target=start_battery_data_publishing)
    battery_thread.daemon = True
    battery_thread.start()

    # Start the MQTT publishing thread
    mqtt_thread = Thread(target=start_publishing)
    mqtt_thread.daemon = True
    mqtt_thread.start()

    try:
        # Keep the main thread alive
        while True:
            mqtt_thread.join(timeout=1)
            battery_thread.join(timeout=1)
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received - sending final broadcast...")
        broadcast_additional_info_updates()
        print("Final broadcast completed")