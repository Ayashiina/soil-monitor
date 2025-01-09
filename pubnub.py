import os
import subprocess
from pubnub.pnconfiguration import PNConfiguration
from pubnub.callbacks import SubscribeCallback
from pubnub.pubnub import PubNub

pnconfig = PNConfiguration()
pnconfig.publish_key = (os.getenv("PUB_KEY"),)
pnconfig.secret_key = (os.getenv("SUB_KEY"),)
pnconfig.user_id = "my_custom_user_id"
pubnub = PubNub(pnconfig)
channel = os.getenv("CHANNEL")

is_script_running = False


def send_status_to_backend(device_id, status):
    print(f"Sending status update for device {device_id}: {status}")


class MySubscribeCallback(SubscribeCallback):
    def message(self, pubnub, message):
        global is_script_running
        print(f"Received message: {message.message}")

        if message.message["action"] == "start":
            if not is_script_running:
                print(f"Starting monitoring for device {message.message['device_id']}")
                subprocess.Popen(
                    ["python3", "/home/pi/soil_measure.py"]
                )  # Start the monitoring script
                is_script_running = True
                send_status_to_backend(message.message["device_id"], True)
            else:
                print("Script is already running.")

        elif message.message["action"] == "stop":
            if is_script_running:
                print(f"Stopping monitoring for device {message.message['device_id']}")
                os.system(
                    "pkill -f /home/pi/soil_measure.py"
                )  # Stop the monitoring script
                is_script_running = False
                send_status_to_backend(message.message["device_id"], False)
            else:
                print("Script is not running.")


def start_listening():
    print("Starting to listen for PubNub messages...")
    pubnub.subscribe().channels(channel).execute()


if __name__ == "__main__":
    start_listening()
