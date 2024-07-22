"""This code is used to post the data to the oneM2M server. It reads the data from the sensor 
files and sends it to the oneM2M server. It also creates a subscription for notifications."""

import time
import os
import requests
from datetime import datetime


def get_last_line(file_path):
    """This function returns the last line of a given file."""
    with open(file_path, "rb") as f:
        f.seek(-2, os.SEEK_END)
        while f.read(1) != b"\n":
            f.seek(-2, os.SEEK_CUR)
        last_line = f.readline().decode()
    return last_line


def post_to_onem2m(sensor_name, timestamp, sensor1_data, sensor2_data):
    """This function sends sensor data to the oneM2M server."""
    baseurl = "http://127.0.0.1:8080/~/in-cse/in-name/SensorData/data"
    headers = {"X-M2M-Origin": "admin:admin", "Content-Type": "application/xml;ty=4"}
    payload = f"""<?xml version="1.0" encoding="UTF-8"?>
    <m2m:cin xmlns:m2m="http://www.onem2m.org/xml/protocols">
        <cnf>application/xml</cnf>
        <con>&lt;SensorData&gt;
                &lt;Name&gt;{sensor_name}&lt;/Name&gt;
                &lt;Time&gt;{timestamp}&lt;/Time&gt;
                &lt;Sensor1&gt;{sensor1_data}&lt;/Sensor1&gt;
                &lt;Sensor2&gt;{sensor2_data}&lt;/Sensor2&gt;
            &lt;/SensorData&gt;
        </con>
    </m2m:cin>"""
    response = requests.post(baseurl, headers=headers, data=payload)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if response.status_code == 201:
        print(
            f"Data posted successfully for {sensor_name} at {timestamp}. Current time: {current_time}"
        )
    else:
        print(
            f"Failed to post data for {sensor_name}. Status code: {response.status_code}"
        )


def create_subscription(sensor_type, notification_url):
    """This function creates a subscription for notifications."""
    baseurl = "http://127.0.0.1:8080/~/in-cse/in-name/SensorData/data"
    headers = {"X-M2M-Origin": "admin:admin", "Content-Type": "application/xml;ty=23"}
    payload = f"""<?xml version="1.0" encoding="UTF-8"?>
    <m2m:sub xmlns:m2m="http://www.onem2m.org/xml/protocols">
        <rn>{sensor_type}Subscription</rn>
        <nu>{notification_url}</nu>
        <nct>2</nct>
    </m2m:sub>"""
    response = requests.post(baseurl, headers=headers, data=payload)
    if response.status_code == 201:
        print(f"Subscription created successfully for {sensor_type}.")
    else:
        print(
            f"Failed to create subscription for {sensor_type}. Status code: {response.status_code}"
        )
        print(f"Response: {response.text}")


def monitor_files(file_paths, sleep_time=1):
    """This function continuously monitors multiple sensor files for updates and sends it to oneM2M through http request."""
    last_modified_times = {
        file_path: os.path.getmtime(file_path) if os.path.isfile(file_path) else None
        for file_path in file_paths
    }

    sensor_names = {
        "SINK_4.txt": "Airsensordata",
        "SINK_19.txt": "Watersensordata",
        "SINK_20.txt": "Solarsensordata",
        "SINK_21.txt": "CrowdMonitoringsensordata",
        "SINK_22.txt": "RoomMonitoringsensordata",
    }

    while True:
        try:
            for file_path in file_paths:
                if not os.path.isfile(file_path):
                    print(f"File {file_path} does not exist.")
                    continue

                current_modified_time = os.path.getmtime(file_path)
                if (
                    last_modified_times[file_path] is None
                    or current_modified_time != last_modified_times[file_path]
                ):
                    last_modified_times[file_path] = current_modified_time
                    last_line = get_last_line(file_path).strip()
                    data = last_line.split()

                    if len(data) == 3:
                        data = [float(i) for i in data]
                        sensor1_data = data[1]
                        sensor2_data = data[2]
                        timestamp = int(data[0])
                        sensor_name = sensor_names.get(
                            os.path.basename(file_path), "UnknownSensor"
                        )
                        post_to_onem2m(
                            sensor_name, timestamp, sensor1_data, sensor2_data
                        )
                    else:
                        print(
                            f"Unexpected data format in file {file_path}: {last_line}"
                        )
            time.sleep(sleep_time)
        except Exception as e:
            print(f"An error occurred: {e}")
            # Continue monitoring after exception


if __name__ == "__main__":
    create_subscription("SensorData", "http://127.0.0.1:8000/notification")
    file_paths = [
        "SINK_4.txt",
        "SINK_19.txt",
        "SINK_20.txt",
        "SINK_21.txt",
        "SINK_22.txt",
    ]

    file_paths = ["cupcarbon/results/" + file for file in file_paths]

    monitor_files(file_paths)
