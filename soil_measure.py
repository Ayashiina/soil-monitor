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

device_id = 3


def start_listening():
    print("Starting to listen for PubNub messages...")
    pubnub.subscribe().channels(channel).execute()


def check_soil_moisture():
    GPIO.output(LED_PIN, GPIO.HIGH if GPIO.input(SOIL_PIN) else GPIO.LOW)
    return "Dry" if GPIO.input(SOIL_PIN) else "Wet"


def send_data_to_backend(status, device_id):
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
    print("Monitoring soil moisture status...")
    while True:
        status = check_soil_moisture()
        
        if status == "Dry":
            if previous_state != "Dry":
                print("Soil is dry. LED is blinking.")
                send_data_to_backend(status, device_id)
                previous_state = "Dry"

            GPIO.output(LED_PIN, GPIO.HIGH)
            time.sleep(1)
            GPIO.output(LED_PIN, GPIO.LOW)
            time.sleep(1)

        elif status == "Wet":
            if previous_state != "Wet":
                print("Soil is wet. LED is turned off.")
                send_data_to_backend(status, device_id)
                previous_state = "Wet"

            GPIO.output(LED_PIN, GPIO.LOW)

        time.sleep(0.5) 

except KeyboardInterrupt:
    print("Exiting program. Cleaning up GPIO...")
    GPIO.cleanup()