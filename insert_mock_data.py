import mysql.connector
from db import get_db_connection
from datetime import datetime

try:
    connection = get_db_connection()
    cursor = connection.cursor()

    devices_data = [
        ("Sensor A", "Greenhouse"),
        ("Sensor B", "Field 1"),
        ("Sensor C", "Field 2"),
    ]
    cursor.executemany(
        "INSERT INTO devices (name, location) VALUES (%s, %s)", devices_data
    )

    alerts_data = [
        (1, "Dry"),
        (2, "Wet"),
        (3, "Wet"),
        (3, "Dry"),
    ]
    cursor.executemany(
        "INSERT INTO alerts_log (device_id, status) VALUES (%s, %s)",
        alerts_data,
    )

    connection.commit()
    print("Mock data inserted successfully.")

except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("Database connection closed.")
