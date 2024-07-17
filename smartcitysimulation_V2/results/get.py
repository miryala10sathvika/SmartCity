from http.server import HTTPServer, BaseHTTPRequestHandler
from pymongo import MongoClient, InsertOne
import xml.etree.ElementTree as ET
import requests
import json
import threading
import time
from collections import deque
from datetime import datetime
import psutil
import csv

BATCH_INTERVAL = 10  # Interval in seconds for batch processing
BATCH_SIZE = 100  # Maximum batch size for writes

# CPU utilization logging configuration
cpu_log_file = 'onem2m_get_cpu_utilization.csv'
cpu_log_interval = 30  # seconds

# Thread-safe queue for storing data to be written in batches
data_queue = deque()
data_lock = threading.Lock()

# MongoDB client with connection pooling
client = MongoClient('mongodb://localhost:27017/', maxPoolSize=20)
db = client['sensordatabaseversion2']
collection = db['sensordata']

class NotificationHandler(BaseHTTPRequestHandler):
    """This class handles incoming notifications from the oneM2M server."""
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        # Parse the received data and store it in the queue
        sensor_name, timestamp, sensor1_data, sensor2_data = parse_sensor_data(post_data.decode())
        if sensor_name and timestamp:
            with data_lock:
                data_queue.append((sensor_name, timestamp, sensor1_data, sensor2_data))
            send_notification(sensor_name, timestamp, sensor1_data, sensor2_data)
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        # Handle verification GET request
        self.send_response(200)
        self.end_headers()

def start_server():
    """This function starts the HTTP server to receive notifications."""
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, NotificationHandler)
    print("Starting server to receive notifications...")
    httpd.serve_forever()

def parse_sensor_data(data):
    """This function parses the sensor data from the XML string."""
    try:
        root = ET.fromstring(data)
        con = root.find(".//con")
        if con is not None:
            sensor_data_xml = con.text
            sensor_root = ET.fromstring(sensor_data_xml)
            sensor_name = sensor_root.findtext('Name')
            timestamp = sensor_root.findtext('Time')
            sensor1_text = sensor_root.findtext('Sensor1')
            sensor2_text = sensor_root.findtext('Sensor2')
            sensor1_data = float(sensor1_text) if sensor1_text else None
            sensor2_data = float(sensor2_text) if sensor2_text else None
            return sensor_name, timestamp, sensor1_data, sensor2_data
        else:
            print("No sensor data found in the notification")
            return None, None, None, None
    except ET.ParseError as e:
        print(f"Error parsing XML data: {e}")
        return None, None, None, None
    except ValueError as e:
        print(f"Error converting sensor data to float: {e}")
        return None, None, None, None

def send_notification(sensor_name, timestamp, sensor1_data, sensor2_data):
    """This function sends sensor data to the appropriate service based on sensor name."""
    if sensor_name == "Airsensordata":
        threading.Thread(target=send_to_sensor_service, args=("http://localhost:8001/notification", sensor_name, timestamp, sensor1_data, sensor2_data)).start()
    elif sensor_name == "Watersensordata":
        threading.Thread(target=send_to_sensor_service, args=("http://localhost:8002/notification", sensor_name, timestamp, sensor1_data, sensor2_data)).start()
    elif sensor_name == "Solarsensordata":
        threading.Thread(target=send_to_sensor_service, args=("http://localhost:8003/notification", sensor_name, timestamp, sensor1_data, sensor2_data)).start()
    elif sensor_name == "RoomMonitoringsensordata":
        threading.Thread(target=send_to_sensor_service, args=("http://localhost:8004/notification", sensor_name, timestamp, sensor1_data, sensor2_data)).start()
    elif sensor_name == "CrowdMonitoringsensordata":
        threading.Thread(target=send_to_sensor_service, args=("http://localhost:8005/notification", sensor_name, timestamp, sensor1_data, sensor2_data)).start()

def send_to_sensor_service(url, sensor_name, timestamp, sensor1_data, sensor2_data):
    """This function sends sensor data to the specified sensor service."""
    payload = {
        "Name": sensor_name,
        "Time": timestamp,
        "Sensor1": sensor1_data,
        "Sensor2": sensor2_data
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    if response.status_code == 200:
        print(f"Data sent to {url} successfully")
    else:
        print(f"Failed to send data to {url}: {response.status_code}, {response.text}")

def batch_write_to_mongodb():
    """This function writes data to MongoDB in batches."""
    while True:
        time.sleep(BATCH_INTERVAL)
        batch = []
        with data_lock:
            while data_queue and len(batch) < BATCH_SIZE:
                batch.append(data_queue.popleft())
        if batch:
            print(f"Writing batch of {len(batch)} records to MongoDB...")
            try:
                requests = [InsertOne({
                    '_id': f"{sensor_name}_{timestamp}",
                    sensor_name: {'value1': sensor1_data, 'value2': sensor2_data}
                }) for sensor_name, timestamp, sensor1_data, sensor2_data in batch]
                collection.bulk_write(requests)
                print("Batch write complete.")
            except Exception as e:
                print(f"Error during batch write to MongoDB: {e}")

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
    # Start the batch writing thread
    threading.Thread(target=batch_write_to_mongodb, daemon=True).start()
    # Start the CPU utilization logging thread
    threading.Thread(target=log_cpu_utilization, daemon=True).start()
    # Start the HTTP server
    start_server()
