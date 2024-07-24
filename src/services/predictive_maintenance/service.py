# This service uses data from the Environmental Quality Index Service,
# Energy Optimization Service, and Anomaly Detection Service to forecast when maintenance may be
# required. It also uses the Notification Service to send out alerts when maintenance is required.

from flask import Flask, request, jsonify
import requests
import numpy as np
from scipy import stats

app = Flask(__name__)

SERVICES = {
    "environmental_quality": "http://localhost:8006/environmental_quality_index",
    "energy_optimization": "http://localhost:8007/energy_optimization",
    "anomaly_detection": "http://localhost:8009/detect_anomalies",
    "notification": "http://localhost:8010/notify",
}


def get_service_data(service, params=None):
    try:
        response = requests.get(SERVICES[service], params=params)
        return response.json()
    except requests.RequestException:
        return None


def send_notification(service, message):
    try:
        requests.post(
            SERVICES["notification"], json={"service": service, "message": message}
        )
    except requests.RequestException:
        pass  # TODO: handle proper error


@app.route("/predict_maintenance", methods=["GET"])
def predict_maintenance():
    # Get data from other services
    env_quality = get_service_data(
        "environmental_quality", {"air_id": "1", "water_id": "1"}
    )
    energy_data = get_service_data(
        "energy_optimization", {"solar_id": "1", "room_id": "1"}
    )
    anomalies = get_service_data("anomaly_detection")

    maintenance_score = 0
    reasons = []

    if env_quality:
        if env_quality["environmental_quality_index"] < 50:
            maintenance_score += 1
            reasons.append("Poor environmental quality")

    if energy_data:
        if energy_data["energy_surplus"] < 0:
            maintenance_score += 1
            reasons.append("Energy deficit")

    if anomalies and anomalies.get("anomalies"):
        maintenance_score += len(anomalies["anomalies"])
        reasons.append(f"Detected {len(anomalies['anomalies'])} anomalies")

    if maintenance_score > 2:
        prediction = "Maintenance recommended"
        send_notification(
            "maintenance", f"Maintenance recommended. Reasons: {', '.join(reasons)}"
        )
    elif maintenance_score > 0:
        prediction = "Monitor closely"
    else:
        prediction = "No maintenance needed"

    return jsonify(
        {
            "prediction": prediction,
            "maintenance_score": maintenance_score,
            "reasons": reasons,
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8011)
