from http.server import HTTPServer, BaseHTTPRequestHandler
from pymongo import MongoClient
import xml.etree.ElementTree as ET
from datetime import datetime
import requests
import json
import threading
from common import store_to_mongodb
import psutil
import csv
import time


# CPU utilization logging configuration
cpu_log_file = 'onem2m_get_cpu_utilization.csv'
cpu_log_interval = 30  # seconds

class NotificationHandler(BaseHTTPRequestHandler):
    """This class handles incoming notifications from the oneM2M server."""
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        # Parse the received data and store it in MongoDB
        sensor_name, timestamp, sensor1_data, sensor2_data = parse_sensor_data(post_data.decode())
        if sensor_name and timestamp:
            store_to_mongodb(sensor_name, timestamp, sensor1_data, sensor2_data)
            if sensor_name == "Airsensordata":
                # send_to_air_sensor_service(sensor_name, timestamp, sensor1_data, sensor2_data)
                threading.Thread(target=send_to_air_sensor_service, args=(sensor_name, timestamp, sensor1_data, sensor2_data)).start()
            elif sensor_name == "Watersensordata":
                # send_to_water_sensor_service(sensor_name, timestamp, sensor1_data, sensor2_data)
                threading.Thread(target=send_to_water_sensor_service, args=(sensor_name, timestamp, sensor1_data, sensor2_data)).start()
            elif sensor_name == "Solarsensordata":
                threading.Thread(target=send_to_solar_sensor_service, args=(sensor_name, timestamp, sensor1_data, sensor2_data)).start()
            elif sensor_name == "RoomMonitoringsensordata":
                threading.Thread(target=send_to_room_monitoring_sensor_service, args=(sensor_name, timestamp, sensor1_data, sensor2_data)).start()
            elif sensor_name == "CrowdMonitoringsensordata":
                threading.Thread(target=send_to_crowd_monitoring_sensor_service, args=(sensor_name, timestamp, sensor1_data, sensor2_data)).start()
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



def send_to_air_sensor_service(sensor_name, timestamp, sensor1_data, sensor2_data):
    """This function sends air sensor data to the air sensor service."""
    url = "http://localhost:8001/notification"
    payload = {
        "Name": sensor_name,
        "Time": timestamp,
        "Sensor1": sensor1_data,
        "Sensor2": sensor2_data
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    if response.status_code == 200:
        print("Data sent to air sensor service successfully")
    else:
        print(f"Failed to send data to air sensor service: {response.status_code}, {response.text}")

def send_to_water_sensor_service(sensor_name, timestamp, sensor1_data, sensor2_data):
    """This function sends water sensor data to the water sensor service."""
    url = "http://localhost:8002/notification"
    payload = {
        "Name": sensor_name,
        "Time": timestamp,
        "Sensor1": sensor1_data,
        "Sensor2": sensor2_data
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    if response.status_code == 200:
        print("Data sent to water sensor service successfully")
    else:
        print(f"Failed to send data to water sensor service: {response.status_code}, {response.text}")

def send_to_solar_sensor_service(sensor_name, timestamp, sensor1_data, sensor2_data):
    """This function sends solar sensor data to the solar sensor service."""
    url = "http://localhost:8003/notification"
    payload = {
        "Name": sensor_name,
        "Time": timestamp,
        "Sensor1": sensor1_data,
        "Sensor2": sensor2_data
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    if response.status_code == 200:
        print("Data sent to solar sensor service successfully")
    else:
        print(f"Failed to send data to solar sensor service: {response.status_code}, {response.text}")

def send_to_room_monitoring_sensor_service(sensor_name, timestamp, sensor1_data, sensor2_data):
    """This function sends room monitoring sensor data to the room monitoring sensor service."""
    url = "http://localhost:8004/notification"
    payload = {
        "Name": sensor_name,
        "Time": timestamp,
        "Sensor1": sensor1_data,
        "Sensor2": sensor2_data
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    if response.status_code == 200:
        print("Data sent to room monitoring sensor service successfully")
    else:
        print(f"Failed to send data to room monitoring sensor service: {response.status_code}, {response.text}")

def send_to_crowd_monitoring_sensor_service(sensor_name, timestamp, sensor1_data, sensor2_data):
    """This function sends crowd monitoring sensor data to the crowd monitoring sensor service."""
    url = "http://localhost:8005/notification"
    payload = {
        "Name": sensor_name,
        "Time": timestamp,
        "Sensor1": sensor1_data,
        "Sensor2": sensor2_data
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    if response.status_code == 200:
        print("Data sent to crowd monitoring sensor service successfully")
    else:
        print(f"Failed to send data to crowd monitoring sensor service: {response.status_code}, {response.text}")

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
    start_server()