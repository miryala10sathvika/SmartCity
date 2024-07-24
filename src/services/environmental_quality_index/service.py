from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

AIR_SERVICE_URL = "http://localhost:8001/get_data/"
WATER_SERVICE_URL = "http://localhost:8002/get_data/"


def get_sensor_data(url, sensor_id):
    response = requests.get(f"{url}{sensor_id}")
    if response.status_code == 200:
        return response.json()["data"]
    return None


@app.route("/environmental_quality_index", methods=["GET"])
def get_environmental_quality_index():
    air_id = request.args.get("air_id")
    water_id = request.args.get("water_id")

    air_data = get_sensor_data(AIR_SERVICE_URL, air_id)
    water_data = get_sensor_data(WATER_SERVICE_URL, water_id)

    if air_data and water_data:
        air_quality = float(air_data["Sensor1"])
        water_quality = float(water_data["Sensor1"])

        # Simple index calculation
        # TODO: Improve this calculation
        eqi = (air_quality + water_quality) / 2

        return jsonify(
            {
                "environmental_quality_index": eqi,
                "air_quality": air_quality,
                "water_quality": water_quality,
            }
        )
    else:
        return jsonify({"error": "Unable to fetch sensor data"}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8006)
