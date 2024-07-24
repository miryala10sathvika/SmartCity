from flask import Flask, request, jsonify
import requests
import numpy as np

app = Flask(__name__)

SENSOR_SERVICES = {
    "air": "http://localhost:8001/get_data/",
    "water": "http://localhost:8002/get_data/",
    "solar": "http://localhost:8003/get_data/",
    "room": "http://localhost:8004/get_data/",
    "crowd": "http://localhost:8005/get_data/",
}


def get_sensor_data(url, sensor_id):
    response = requests.get(f"{url}{sensor_id}")
    if response.status_code == 200:
        return response.json()["data"]
    return None


def is_anomaly(value, mean, std_dev):
    return abs(value - mean) > 2 * std_dev


@app.route("/detect_anomalies", methods=["POST"])
def detect_anomalies():
    data = request.json
    anomalies = {}

    for sensor_type, sensor_ids in data.items():
        if sensor_type not in SENSOR_SERVICES:
            continue

        values = []
        for sensor_id in sensor_ids:
            sensor_data = get_sensor_data(SENSOR_SERVICES[sensor_type], sensor_id)
            if sensor_data:
                values.append(float(sensor_data["Sensor1"]))

        if values:
            mean = np.mean(values)
            std_dev = np.std(values)

            for sensor_id, value in zip(sensor_ids, values):
                if is_anomaly(value, mean, std_dev):
                    if sensor_type not in anomalies:
                        anomalies[sensor_type] = []
                    anomalies[sensor_type].append(
                        {
                            "sensor_id": sensor_id,
                            "value": value,
                            "mean": mean,
                            "std_dev": std_dev,
                        }
                    )

    return jsonify({"anomalies": anomalies})


def run():
    app.run(host="0.0.0.0", port=8009)


if __name__ == "__main__":
    run()
