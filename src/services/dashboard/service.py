from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

SERVICES = {
    "environmental_quality": "http://localhost:8006/environmental_quality_index",
    "energy_optimization": "http://localhost:8007/energy_optimization",
    "crowd_management": "http://localhost:8008/crowd_management",
    "anomaly_detection": "http://localhost:8009/detect_anomalies",
    "predictive_maintenance": "http://localhost:8011/predict_maintenance",
}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/dashboard_data")
def dashboard_data():
    data = {}
    for service, url in SERVICES.items():
        try:
            response = requests.get(url)
            data[service] = response.json()
        except requests.RequestException:
            data[service] = {"error": "Service unavailable"}
    return jsonify(data)


def run():
    app.run(host="0.0.0.0", port=8012)


if __name__ == "__main__":
    run()
