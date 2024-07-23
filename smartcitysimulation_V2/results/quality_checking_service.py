from flask import Blueprint, request, jsonify
from pymongo import MongoClient

environment_quality_bp = Blueprint('environment_quality', __name__)

# MongoDB client
mongo_client = MongoClient('mongodb://localhost:27017/', maxPoolSize=20)

# Mapping of sensor names to MongoDB collection names
sensor_mapping = {
    "air": "Airsensordata",
    "water": "Watersensordata",
    "solar": "Solarsensordata",
    "room": "RoomMonitoringsensordata",
    "crowd": "CrowdMonitoringsensordata"
}

@environment_quality_bp.route('/check_quality', methods=['POST'])
def check_quality():
    data = request.json
    sensors = data.get('sensors')
    timestamp = data.get('timestamp')
    location = data.get('location')

    if not sensors or not timestamp or not location:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    results = {}
    try:
        for sensor in sensors:
            sensor_name = sensor_mapping.get(sensor)
            if not sensor_name:
                return jsonify({"status": "error", "message": f"Invalid sensor type: {sensor}"}), 400
            
            db = mongo_client['sensordatabaseversion2']
            collection = db['sensordata']
            document = collection.find_one({"_id": f"{sensor_name}_{timestamp}"})

            if document and sensor_name in document:
                sensor_data = document[sensor_name]
                value_key = f"value{location[-1]}"  # Assuming location is in format 'room1', 'room2', etc.
                value = sensor_data.get(value_key, float('inf'))
                
                if value < 100:
                    results[sensor] = f"Quality is good at {location}"
                else:
                    results[sensor] = f"Quality is bad at {location}"
            else:
                results[sensor] = f"No data found for the specified timestamp and location {location}"

        return jsonify({"status": "success", "data": results}), 200
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
