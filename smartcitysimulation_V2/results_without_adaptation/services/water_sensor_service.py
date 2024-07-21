from flask import Flask, request, jsonify
from datetime import datetime
import psutil
import sqlite3
import threading
import csv
import time

app = Flask(__name__)
process = psutil.Process()

# CPU utilization logging configuration
cpu_log_file = 'water_cpu_utilization.csv'
cpu_log_interval = 30  # seconds

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('watersensor_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS watersensordata (
                        _id TEXT PRIMARY KEY,
                        value1 REAL,
                        value2 REAL
                      )''')
    conn.commit()
    conn.close()

init_db()

@app.route('/notification', methods=['POST'])
def handle_notification():
    global batch_processing_mode, batch_data
    try:
        data = request.json
        sensor_name = data.get('Name')
        timestamp = data.get('Time')
        sensor1_data = data.get('Sensor1')
        sensor2_data = data.get('Sensor2')
        
        if sensor_name and timestamp:
            store_to_sqlite('watersensordata', sensor_name, timestamp, sensor1_data, sensor2_data)
            return jsonify({"status": "success", "message": "Data stored successfully"}), 200
        else:
            return jsonify({"status": "error", "message": "Invalid sensor data"}), 400
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_data/<id>', methods=['GET'])
def get_data(id):
    global failure_count, batch_processing_mode
    try:  
        # Fetch from SQLite 
        data = fetch_from_sqlite('watersensordata', id)
        if data:
            return jsonify({"status": "success", "data": data}), 200
        else:
            return jsonify({"status": "error", "message": "Data not found"}), 404
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def store_to_sqlite(table_name, sensor_name, timestamp, sensor1_data, sensor2_data):
    """This function stores the given data into the specified SQLite table."""
    try:
        conn = sqlite3.connect('watersensor_data.db')
        cursor = conn.cursor()
        cursor.execute(f'''INSERT OR REPLACE INTO {table_name} (_id, value1, value2)
                           VALUES (?, ?, ?)''', (timestamp, sensor1_data, sensor2_data))
        conn.commit()
        conn.close()
        print(f"Data stored successfully for {sensor_name} at {timestamp}")
    except Exception as e:
        print(f"Error storing data to SQLite: {e}")

def fetch_from_sqlite(table_name, id):
    """This function fetches the data from the specified SQLite table using the provided ID."""
    try:
        conn = sqlite3.connect('watersensor_data.db')
        cursor = conn.cursor()
        cursor.execute(f'''SELECT _id, value1, value2 FROM {table_name} WHERE _id = ?''', (id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "Time": row[0],
                "Sensor1": row[1],
                "Sensor2": row[2]
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

if __name__ == "__main__":
    # Start the CPU utilization logging thread
    threading.Thread(target=log_cpu_utilization, daemon=True).start()
    app.run(host='0.0.0.0', port=8002)
