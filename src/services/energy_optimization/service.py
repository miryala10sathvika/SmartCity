from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

SOLAR_SERVICE_URL = "http://localhost:8003/get_data/"
ROOM_SERVICE_URL = "http://localhost:8004/get_data/"


def get_sensor_data(url, sensor_id):
    response = requests.get(f"{url}{sensor_id}")
    if response.status_code == 200:
        return response.json()["data"]
    return None


@app.route("/energy_optimization", methods=["GET"])
def get_energy_optimization():
    solar_id = request.args.get("solar_id")
    room_id = request.args.get("room_id")

    solar_data = get_sensor_data(SOLAR_SERVICE_URL, solar_id)
    room_data = get_sensor_data(ROOM_SERVICE_URL, room_id)

    if solar_data and room_data:
        solar_output = float(solar_data["Sensor1"])
        room_energy_consumption = float(room_data["Sensor1"])

        energy_surplus = solar_output - room_energy_consumption
        optimization_recommendation = (
            "Optimal" if energy_surplus >= 0 else "Reduce consumption"
        )

        return jsonify(
            {
                "energy_surplus": energy_surplus,
                "solar_output": solar_output,
                "room_energy_consumption": room_energy_consumption,
                "optimization_recommendation": optimization_recommendation,
            }
        )
    else:
        return jsonify({"error": "Unable to fetch sensor data"}), 400


def run():
    app.run(host="0.0.0.0", port=8007)


if __name__ == "__main__":
    run()
