from flask import Blueprint, request, jsonify
from datetime import datetime
import psutil
import atexit
import sqlite3
from collections import OrderedDict
import threading
import time
from cachetools import LRUCache
import csv
import os

air_blueprint = Blueprint('air', __name__)
process = psutil.Process()

# recently added configuration
RECENT_CACHE_SIZE = 50
recent_cache = OrderedDict()

# Batch processing configuration
batch_data = []
batch_lock = threading.Lock()

get_data_cache = LRUCache(maxsize=100)

# CPU utilization logging configuration
cpu_log_file = 'air_cpu_utilization.csv'
cpu_log_interval = 30  # seconds

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('airsensor_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Airsensordata (
                        _id TEXT PRIMARY KEY,
                        value1 REAL,
                        location1 TEXT,
                        value2 REAL,
                        location2 TEXT
                      )''')
    conn.commit()
    conn.close()

init_db()

def batch_write():
    global batch_data
    while True:
        time.sleep(10)
        with batch_lock:
            if batch_data:
                try:
                    conn = sqlite3.connect('airsensor_data.db')
                    cursor = conn.cursor()
                    cursor.executemany('''INSERT OR REPLACE INTO Airsensordata (_id, value1, location1, value2, location2)
                                          VALUES (?, ?, ?, ?, ?)''', batch_data)
                    conn.commit()
                    conn.close()
                    print(f"Batch write successful: {len(batch_data)} records")
                    batch_data.clear()
                except Exception as e:
                    print(f"Error during batch write: {e}")

# Start batch write thread
threading.Thread(target=batch_write, daemon=True).start()

@air_blueprint.route('/notification', methods=['POST'])
def handle_notification():
    global batch_data 
    try:
        data = request.json
        sensor_name = data.get('Name')
        timestamp = data.get('Time')
        sensor1_data = data.get('Sensor1')
        sensor1_location = data.get('Sensor1Location')
        sensor2_data = data.get('Sensor2')
        sensor2_location = data.get('Sensor2Location')

        if sensor_name and timestamp:
            with batch_lock:
                batch_data.append((timestamp, sensor1_data, sensor1_location, sensor2_data, sensor2_location))
            print(f"Batching data for {sensor_name} at {timestamp}")

            # Store data in cache
            cache_key = f"{sensor_name}_{timestamp}"
            if len(recent_cache) >= RECENT_CACHE_SIZE:
                recent_cache.popitem(last=False)  # Remove the oldest item
            recent_cache[cache_key] = {
                "Name": sensor_name,
                "Time": timestamp,
                "Sensor1": sensor1_data,
                "Sensor1Location": sensor1_location,
                "Sensor2": sensor2_data,
                "Sensor2Location": sensor2_location
            }

            return jsonify({"status": "success", "message": "Data stored successfully"}), 200
        else:
            return jsonify({"status": "error", "message": "Invalid sensor data"}), 400
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@air_blueprint.route('/get_data/<id>', methods=['GET'])
def get_data(id):
    global batch_data
    try:
        if id in get_data_cache:
            return jsonify({"status": "success", "data": get_data_cache[id]}), 200
        
        # Check in cache first
        if id in recent_cache:
            get_data_cache[id] = recent_cache[id]
            return jsonify({"status": "success", "data": recent_cache[id]}), 200
        
        # Fetch from SQLite if not in cache
        data = fetch_from_sqlite('Airsensordata', id)
        if data:
            get_data_cache[id] = data
            return jsonify({"status": "success", "data": data}), 200
        else:
            return jsonify({"status": "error", "message": "Data not found"}), 404
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def fetch_from_sqlite(table_name, id):
    """This function fetches the data from the specified SQLite table using the provided ID."""
    try:
        conn = sqlite3.connect('airsensor_data.db')
        cursor = conn.cursor()
        cursor.execute(f'''SELECT _id, value1, location1, value2, location2 FROM {table_name} WHERE _id = ?''', (id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "Time": row[0],
                "Sensor1": row[1],
                "Sensor1Location": row[2],
                "Sensor2": row[3],
                "Sensor2Location": row[4]
            }
        return None
    except Exception as e:
        print(f"Error fetching data from SQLite: {e}")
        return None

def log_cpu_utilization():
    """This function logs CPU utilization to a CSV file every 30 seconds."""
    with open(cpu_log_file, 'w', newline='') as csvfile:
        fieldnames = ['Timestamp', 'CPU Utilization']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        while True:
            cpu_usage = psutil.cpu_percent(interval=1)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow({'Timestamp': timestamp, 'CPU Utilization': cpu_usage})
            csvfile.flush()
            time.sleep(cpu_log_interval - 1)  # Subtract the interval time used by psutil.cpu_percent

# Start the CPU utilization logging thread
threading.Thread(target=log_cpu_utilization, daemon=True).start()
