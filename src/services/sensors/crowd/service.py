from flask import Flask, request, jsonify
from datetime import datetime
import psutil
import csv
from pymongo import MongoClient, InsertOne
from collections import OrderedDict
import threading
import time
from cachetools import LRUCache

app = Flask(__name__)
process = psutil.Process()

# Cache configuration
RECENT_CACHE = 40
recent_cache = OrderedDict()

# MongoDB client
mongo_client = MongoClient("mongodb://localhost:27017/", maxPoolSize=20)

# Batch processing configuration
batch_data = []
batch_interval = 10  # seconds
batch_lock = threading.Lock()

# Cache for get_data endpoint
get_data_cache = LRUCache(maxsize=100)

# CPU utilization logging configuration
cpu_log_file = "crowd_cpu_utilization.csv"
cpu_log_interval = 30  # seconds


def batch_writer():
    global batch_data
    while True:
        time.sleep(batch_interval)
        with batch_lock:
            if batch_data:
                try:
                    db = mongo_client["crowd_sensor_db"]
                    collection = db["crowdsensordata"]
                    collection.bulk_write(batch_data)
                    print(f"Batch write completed with {len(batch_data)} records.")
                    batch_data = []
                except Exception as e:
                    print(f"Error during batch write: {e}")


# Start the batch writer thread
threading.Thread(target=batch_writer, daemon=True).start()


@app.route("/notification", methods=["POST"])
def handle_notification():
    global batch_data
    try:
        data = request.json
        sensor_name = data.get("Name")
        timestamp = data.get("Time")
        sensor1_data = data.get("Sensor1")
        sensor2_data = data.get("Sensor2")

        if sensor_name and timestamp:
            with batch_lock:
                batch_data.append(
                    InsertOne(
                        {
                            "_id": timestamp,  # Use timestamp as the unique identifier
                            "Name": sensor_name,
                            "Sensor1": sensor1_data,
                            "Sensor2": sensor2_data,
                        }
                    )
                )
            # Store data in recent_cache
            recent_cache_key = timestamp
            if len(recent_cache) >= RECENT_CACHE:
                recent_cache.popitem(last=False)  # Remove the oldest item
            recent_cache[recent_cache_key] = {
                "Name": sensor_name,
                "Time": timestamp,
                "Sensor1": sensor1_data,
                "Sensor2": sensor2_data,
            }
            return jsonify({"status": "success", "message": "Data added to batch"}), 200
        else:
            return jsonify({"status": "error", "message": "Invalid sensor data"}), 400
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/get_data/<id>", methods=["GET"])
def get_data(id):
    global failure_count
    try:
        if id in get_data_cache:
            return jsonify({"status": "success", "data": get_data_cache[id]}), 200

        # Check in recent_cache first
        if id in recent_cache:
            get_data_cache[id] = recent_cache[id]
            return jsonify({"status": "success", "data": recent_cache[id]}), 200

        # Fetch from MongoDB if not in recent_cache
        data = fetch_from_mongodb("crowd_sensor_db", "crowdsensordata", id)
        if data:
            get_data_cache[id] = data
            return jsonify({"status": "success", "data": data}), 200
        else:
            failure_count += 1
            return jsonify({"status": "error", "message": "Data not found"}), 404
    except Exception as e:
        print(f"An error occurred: {e}")
        failure_count += 1
        return jsonify({"status": "error", "message": str(e)}), 500


def fetch_from_mongodb(db_name, collection_name, id):
    """This function fetches the data from the specified MongoDB collection using the provided ID."""
    try:
        db = mongo_client[db_name]
        collection = db[collection_name]
        data = collection.find_one({"_id": id}, {"_id": 0})
        return data
    except Exception as e:
        print(f"Error fetching data from MongoDB: {e}")
        return None


def log_cpu_utilization():
    """This function logs CPU utilization to a CSV file every 30 seconds."""
    with open(cpu_log_file, "w", newline="") as csvfile:
        fieldnames = ["Timestamp", "CPU Utilization"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        while True:
            cpu_usage = psutil.cpu_percent(interval=1)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            writer.writerow({"Timestamp": timestamp, "CPU Utilization": cpu_usage})
            csvfile.flush()
            time.sleep(
                cpu_log_interval - 1
            )  # Subtract the interval time used by psutil.cpu_percent


def run():
    # Start the CPU utilization logging thread
    threading.Thread(target=log_cpu_utilization, daemon=True).start()
    app.run(host="0.0.0.0", port=8005)


if __name__ == "__main__":
    run()
