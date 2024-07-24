from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

CROWD_SERVICE_URL = "http://localhost:8005/get_data/"
ROOM_SERVICE_URL = "http://localhost:8004/get_data/"


def get_sensor_data(url, sensor_id):
    response = requests.get(f"{url}{sensor_id}")
    if response.status_code == 200:
        return response.json()["data"]
    return None


@app.route("/crowd_management", methods=["GET"])
def get_crowd_management():
    crowd_id = request.args.get("crowd_id")
    room_id = request.args.get("room_id")

    crowd_data = get_sensor_data(CROWD_SERVICE_URL, crowd_id)
    room_data = get_sensor_data(ROOM_SERVICE_URL, room_id)

    if crowd_data and room_data:
        crowd_density = float(crowd_data["Sensor1"])
        room_capacity = float(
            room_data["Sensor2"]
        )  # TODO: update this sensor number to match the correct room capacity sensor number

        occupancy_percentage = (
            (crowd_density / room_capacity) * 100 if room_capacity > 0 else 0
        )

        if occupancy_percentage < 50:
            status = "Low occupancy"
        elif 50 <= occupancy_percentage < 80:
            status = "Moderate occupancy"
        else:
            status = "High occupancy"

        return jsonify(
            {
                "occupancy_percentage": occupancy_percentage,
                "crowd_density": crowd_density,
                "room_capacity": room_capacity,
                "status": status,
            }
        )
    else:
        return jsonify({"error": "Unable to fetch sensor data"}), 400


def run():
    app.run(host="0.0.0.0", port=8008)


if __name__ == "__main__":
    run()
