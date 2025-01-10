import os
import subprocess
from pubnub.pnconfiguration import PNConfiguration
from pubnub.callbacks import SubscribeCallback
from pubnub.pubnub import PubNub
from dotenv import load_dotenv

load_dotenv()

pnconfig = PNConfiguration()
pnconfig.publish_key = os.getenv("PUB_KEY")
pnconfig.subscribe_key = os.getenv("SUB_KEY")
pnconfig.user_id = os.getenv("USER_ID")
pubnub = PubNub(pnconfig)
channel = os.getenv("CHANNEL")
is_script_running = False


def send_response_to_backend(status, device_id, message):
    response_message = {"deviceId": device_id, "status": status, "message": message}
    pubnub.publish().channel(channel).message(response_message).sync()


class SoilSubscribeCallback(SubscribeCallback):
    def message(self, pubnub, message):
        global is_script_running
        print(f"Received message: {message.message}")

        if message.message["action"] == "start":
            device_id = message.message["deviceId"]
            print(f"Received 'start' action for device {device_id}")

            if not is_script_running:
                print(f"Starting monitoring for device {device_id}")
                try:
                    print("Attempting to start soil_measure.py...")
                    subprocess.Popen(["python3", "/home/pi/soil_measure.py"])
                    send_response_to_backend(
                        "success",
                        device_id,
                        f"Monitoring started for device {device_id}.",
                    )

                except FileNotFoundError as e:
                    send_response_to_backend(
                        "error", device_id, f"Error: {e}. Script not found."
                    )
                except Exception as e:
                    send_response_to_backend(
                        "error", device_id, f"Unexpected error occurred: {e}"
                    )

                is_script_running = True
            else:
                send_response_to_backend(
                    "error", device_id, "Script is already running."
                )


def start_listening():
    print("Starting to listen for PubNub messages...")
    pubnub.add_listener(SoilSubscribeCallback())
    print("SoilSubscribeCallback added...")
    try:
        pubnub.subscribe().channels(channel).execute()
    except Exception as e:
        print(f"Error while subscribing: {e}")


if __name__ == "__main__":
    start_listening()
