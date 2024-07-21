# air_sensor.py
from flask import Flask, request, jsonify
from datetime import datetime
import psutil
import atexit
from pymongo import MongoClient
from common import store_to_mongodb_sensor

app = Flask(__name__)
process = psutil.Process()


def print_cpu_usage():
    cpu_times = process.cpu_times()
    print(f"Total CPU time used by the program (in seconds): User = {cpu_times.user}, System = {cpu_times.system}")

atexit.register(print_cpu_usage)



@app.route('/notification', methods=['POST'])
def handle_notification():
    try:
        data = request.json
        sensor_name = data.get('Name')
        timestamp = data.get('Time')
        sensor1_data = data.get('Sensor1')
        sensor2_data = data.get('Sensor2')
        
        if sensor_name and timestamp:
            store_to_mongodb_sensor('air_sensor_db', 'airsensordata', sensor_name, timestamp, sensor1_data, sensor2_data)
            return jsonify({"status": "success", "message": "Data stored successfully"}), 200
        else:
            return jsonify({"status": "error", "message": "Invalid sensor data"}), 400
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_data/<id>', methods=['GET'])
def get_data(id):
    try:
        data = fetch_from_mongodb('air_sensor_db', 'airsensordata', id)
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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8001)
                                      