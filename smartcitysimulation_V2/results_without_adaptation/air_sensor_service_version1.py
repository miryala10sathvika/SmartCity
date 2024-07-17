# room_sensor.py
from flask import Flask, request, jsonify
from datetime import datetime
import psutil
from pymongo import MongoClient
from common import store_to_mongodb_sensor
import threading
import csv
import time

app = Flask(__name__)
process = psutil.Process()

# CPU utilization logging configuration
cpu_log_file = 'room_cpu_utilization.csv'
cpu_log_interval = 30  # seconds

@app.route('/notification', methods=['POST'])
def handle_notification():
    try:
        data = request.json
        sensor_name = data.get('Name')
        timestamp = data.get('Time')
        sensor1_data = data.get('Sensor1')
        sensor2_data = data.get('Sensor2')
        
        if sensor_name and timestamp:
            store_to_mongodb_sensor('room_sensor_db', 'roomsensordata', sensor_name, timestamp, sensor1_data, sensor2_data)
            return jsonify({"status": "success", "message": "Data stored successfully"}), 200
        else:
            return jsonify({"status": "error", "message": "Invalid sensor data"}), 400
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_data/<id>', methods=['GET'])
def get_data(id):
    try:
        data = fetch_from_mongodb('room_sensor_db', 'roomsensordata', id)
        if data:
            return jsonify({"status": "success", "data": data}), 200
        else:
            return jsonify({"status": "error", "message": "Data not found"}), 404
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


def fetch_from_mongodb(db_name, collection_name, id):
    """This function fetches the data from the specified MongoDB collection using the provided ID."""
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client[db_name]
        collection = db[collection_name]
        data = collection.find_one({'_id': id}, {'_id': 0})
        return data
    except Exception as e: 
        print(f"Error fetching data from MongoDB: {e}")
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

if __name__ == "__main__":
    # Start the CPU utilization logging thread
    threading.Thread(target=log_cpu_utilization, daemon=True).start()
    app.run(host='0.0.0.0', port=8004)
                                      