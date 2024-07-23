from flask import Blueprint, request, jsonify
import sqlite3
import requests

booking_bp = Blueprint('booking', __name__)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('booking_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Bookings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        location TEXT,
                        start_time TEXT,
                        end_time TEXT
                      )''')
    conn.commit()
    conn.close()

init_db()

@booking_bp.route('/book', methods=['POST'])
def book_location():
    data = request.json
    location = data.get('location')
    start_time = data.get('start_time')
    end_time = data.get('end_time')

    if not location or not start_time or not end_time:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    # Step 1: Check availability
    availability_response = requests.post('http://localhost:8000/booking/check_availability', json=data)
    if availability_response.status_code != 200:
        return availability_response.json(), availability_response.status_code

    # Step 2: Check air quality and room monitoring data
    quality_check_data = {
        "location": location,
        "timestamp": start_time,
        "sensors": ["air", "room"]
    }
    quality_response = requests.post('http://localhost:8000/environment/check_quality', json=quality_check_data)
    if quality_response.status_code != 200:
        return quality_response.json(), quality_response.status_code

    quality_results = quality_response.json().get('data', {})
    print(quality_results)
    print(f"Quality is good at {location}")
    if quality_results.get('air') != f"Quality is good at {location}" or quality_results.get('room') != f"Quality is good at {location}":
        return jsonify({"status": "error", "message": "Air quality or room conditions are not suitable"}), 409

    # Step 3: Book the location
    try:
        conn = sqlite3.connect('booking_data.db')
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO Bookings (location, start_time, end_time) VALUES (?, ?, ?)''', (location, start_time, end_time))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Location booked successfully"}), 200
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@booking_bp.route('/check_availability', methods=['POST'])
def check_availability():
    data = request.json
    location = data.get('location')
    start_time = data.get('start_time')
    end_time = data.get('end_time')

    if not location or not start_time or not end_time:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    try:
        conn = sqlite3.connect('booking_data.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT COUNT(*) FROM Bookings
                          WHERE location = ? AND
                                (start_time BETWEEN ? AND ? OR end_time BETWEEN ? AND ? OR
                                 ? BETWEEN start_time AND end_time OR ? BETWEEN start_time AND end_time)''',
                       (location, start_time, end_time, start_time, end_time, start_time, end_time))
        count = cursor.fetchone()[0]
        conn.close()
        if count > 0:
            return jsonify({"status": "error", "message": "Location is already booked for the requested time"}), 409
        else:
            return jsonify({"status": "success", "message": "Location is available"}), 200
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
