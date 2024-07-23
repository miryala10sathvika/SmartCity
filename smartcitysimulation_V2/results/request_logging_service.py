from flask import Blueprint, request, jsonify
from pymongo import MongoClient, UpdateOne
from datetime import datetime

request_logging_bp = Blueprint('request_logging', __name__)

# MongoDB client
mongo_client = MongoClient('mongodb://localhost:27017/', maxPoolSize=20)
db = mongo_client['user_requests_db']
collection = db['user_requests']

@request_logging_bp.route('/log_request', methods=['POST'])
def log_request():
    data = request.json
    user_id = data.get('user_id')
    request_details = data.get('request_details')
    routes = data.get('routes')  # List of route names

    if not user_id or not request_details or not routes:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    try:
        # Add a timestamp and request details to each route
        timestamped_routes = [{"route": route, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "request_details": request_details} for route in routes]

        # Check if user_id already exists in the database
        existing_user = collection.find_one({"user_id": user_id})
        if existing_user:
            # Update the existing document with new routes
            collection.update_one(
                {"user_id": user_id},
                {"$push": {"routes": {"$each": timestamped_routes}},
                 "$set": {"request_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}}
            )
        else:
            # Insert new document if user_id does not exist
            request_entry = {
                "user_id": user_id,
                "request_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "request_details": request_details,
                "routes": timestamped_routes
            }
            collection.insert_one(request_entry)

        return jsonify({"status": "success", "message": "Request logged successfully"}), 200
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
