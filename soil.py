import time
import RPi.GPIO as GPIO
from dotenv import load_dotenv
import os
from pubnub import Pubnub

# Pin setup
SOIL_SENSOR_PIN = 17  
LED_PIN = 18  
BUZZER_PIN = 22  

# PubNub keys
load_dotenv()
PUBNUB_PUBLISH_KEY = os.getenv("PUBNUB_PUBLISH_KEY")
PUBNUB_SUBSCRIBE_KEY = os.getenv("PUBNUB_SUBSCRIBE_KEY")
CHANNEL = os.getenv("CHANNEL")

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(SOIL_SENSOR_PIN, GPIO.IN)

# PubNub client initialization
pubnub = Pubnub(publish_key=PUBNUB_PUBLISH_KEY, subscribe_key=PUBNUB_SUBSCRIBE_KEY)

def read_soil_moisture():
    return GPIO.input(SOIL_SENSOR_PIN)

def send_data_to_cloud(moisture_level):
    pubnub.publish(channel=CHANNEL, message={'moisture': moisture_level})

try:
    while True:
        moisture = read_soil_moisture()
        print(f"Moisture Level: {moisture}")

        # Send data to the cloud server
        send_data_to_cloud(moisture)

        # Control LED/Buzzer based on moisture level
        if moisture == GPIO.LOW:  # Dry soil
            GPIO.output(LED_PIN, GPIO.HIGH) 
            GPIO.output(BUZZER_PIN, GPIO.LOW)
        else:  # Moist soil
            GPIO.output(LED_PIN, GPIO.LOW)  
            GPIO.output(BUZZER_PIN, GPIO.HIGH)  

        time.sleep(5)  

except KeyboardInterrupt:
    print("Program stopped.")
    GPIO.cleanup()
