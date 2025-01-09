import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="soilmeasurement.c9m8a4s4ubga.us-east-1.rds.amazonaws.com",
            user=os.getenv("DB_USER"),
            password="soilmeasurement",
            database="soil_monitor",
        )
        if connection.is_connected():
            return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


connection = get_db_connection()

if connection:
    connection.close()
