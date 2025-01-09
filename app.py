import os
import mysql.connector
from flask import Flask, render_template, jsonify, request
from db import get_db_connection
from flask_cors import CORS
from pubnub.pnconfiguration import PNConfiguration
from pubnub.callbacks import SubscribeCallback
from pubnub.pubnub import PubNub
import json
import subprocess
from dotenv import load_dotenv
import uuid

load_dotenv()

app = Flask(__name__)
CORS(app)

pnconfig = PNConfiguration()
pnconfig.publish_key = (os.getenv("PUB_KEY"),)
pnconfig.subscribe_key = (os.getenv("SUB_KEY"),)
pnconfig.secret_key = (os.getenv("SEC_KEY"),)
pnconfig.user_id = str(uuid.uuid4())
pubnub = PubNub(pnconfig)
channel = os.getenv("CHANNEL")

monitoring_process = None


# Backend Routes
@app.route("/")
def navigation():
    return render_template("navigation.html")


def get_data(table_name):
    connection = get_db_connection()
    if connection is None:
        return {"error": "Failed to connect to the database"}
    cursor = connection.cursor(dictionary=True)

    try:
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)
        data = cursor.fetchall()
        return data
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return {"error": "Database query failed"}
    finally:
        cursor.close()
        connection.close()


@app.route("/devices", methods=["GET"])
def devices():
    return jsonify(get_data("devices"))


@app.route("/alerts", methods=["GET", "POST"])
def alerts():
    return jsonify(get_data("alerts_log"))


# Frontend + RPI Routes
@app.route("/soil-data", methods=["POST"])
def save_soil_data():
    try:
        data = request.json
        device_id = data["device_id"]
        status = data["status"]

        connection = get_db_connection()
        if connection is None:
            return {"error": "Failed to connect to the database"}
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            INSERT INTO alerts_log (device_id, status)
            VALUES (%s, %s)
        """,
            (device_id, status),
        )
        connection.commit()
        connection.close()

        return jsonify({"message": "Data saved successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/add-device", methods=["POST"])
def add_device():
    try:
        data = request.json
        device_name = data["name"]
        device_location = data["location"]

        connection = get_db_connection()
        if connection is None:
            return {"error": "Failed to connect to the database"}

        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO devices (name, location) VALUES (%s, %s)",
            (device_name, device_location),
        )
        connection.commit()
        connection.close()

        return jsonify({"message": "Device added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/monitoring-status", methods=["POST"])
def monitoring_status():
    try:
        data = request.json
        device_id = data["device_id"]
        status = data["status"]
        if status:
            return (
                jsonify({"message": f"Monitoring started for device {device_id}."}),
                200,
            )
        else:
            return (
                jsonify({"message": f"Monitoring stopped for device {device_id}."}),
                200,
            )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/start-monitoring", methods=["POST"])
def start_monitoring():
    try:
        data = request.json
        action = data["action"]
        device_id = data["device_id"]
        print(f"Action: {action}, Device ID: {device_id}")

        if action == "start":
            print(f"Sending 'start' message for device ID: {device_id}")
            message = {
                "action": "start",
                "device_id": device_id,
            }
            response = pubnub.publish().channel(channel).message(message).sync()
            if response.status == 200:
                print(f"Message sent successfully to channel {channel}")
            else:
                print(
                    f"Failed to send message. Status: {response.status}, Message: {response.error_data}"
                )

            return jsonify(
                {"message": f"Monitoring started for device ID {device_id}."}
            )

        elif action == "stop":
            print(f"Sending 'stop' message for device ID: {device_id}")
            message = {
                "action": "stop",
                "device_id": device_id,
            }
            response = pubnub.publish().channel(channel).message(message).sync()

            if response.status == 200:
                print(f"Message sent successfully to channel {channel}")
            else:
                print(
                    f"Failed to send message. Status: {response.status}, Message: {response.error_data}"
                )

            return jsonify(
                {"message": f"Monitoring stopped for device ID {device_id}."}
            )

        else:
            return jsonify({"error": "Invalid action."}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


class SoilSubscribeCallback(SubscribeCallback):
    def message(self, pubnub, message):
        print(f"Backend received response: {message.message}")


def start_listening():
    print("Backend is now listening for Pi responses...")
    pubnub.add_listener(SoilSubscribeCallback())
    pubnub.subscribe().channels(channel).execute()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    start_listening()
