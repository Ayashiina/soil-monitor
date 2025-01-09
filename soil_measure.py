import RPi.GPIO as GPIO
import time
import requests
from dotenv import load_dotenv
import os

GPIO.setmode(GPIO.BCM)
LED_PIN = 26
SOIL_PIN = 21

GPIO.setup(SOIL_PIN, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)

load_dotenv()
previous_state = None
backend_url = os.getenv("BACKEND_URL")


def start_listening():
    print("Starting to listen for PubNub messages...")
    pubnub.subscribe().channels(channel).execute()


def check_soil_moisture():
    return "Dry" if GPIO.input(SOIL_PIN) else "Wet"


def send_data_to_backend(status):
    data = {
        "device_id": device_id,
        "status": status,
    }
    try:
        response = requests.post(backend_url, json=data)
        if response.status_code in (200, 201):
            print("Data saved successfully to the backend!")
        else:
            print(f"Failed to save data to the backend: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending data to backend: {e}")


def blink_led(frequency):
    GPIO.output(LED_PIN, GPIO.HIGH)
    time.sleep(frequency)
    GPIO.output(LED_PIN, GPIO.LOW)
    time.sleep(frequency)


try:
    while True:
        status = check_soil_moisture()
        if status != previous_state:
            if status == "Dry":
                blink_led(frequency=1)
            elif status == "Wet":
                GPIO.output(LED_PIN, GPIO.LOW)

            send_data_to_backend(status)
            previous_state = status

        time.sleep(2)

except KeyboardInterrupt:
    GPIO.cleanup()
