from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# TODO: create endpoints for each service to handle notifications
NOTIFICATION_CHANNELS = {
    "air": "http://localhost:8001/notify",
    "water": "http://localhost:8002/notify",
    "solar": "http://localhost:8003/notify",
    "room": "http://localhost:8004/notify",
    "crowd": "http://localhost:8005/notify",
}


@app.route("/notify", methods=["POST"])
def send_notification():
    data = request.json
    service = data.get("service")
    message = data.get("message")

    if not service or not message:
        return jsonify({"error": "Missing service or message"}), 400

    if service not in NOTIFICATION_CHANNELS:
        return jsonify({"error": "Invalid service"}), 400

    try:
        response = requests.post(
            NOTIFICATION_CHANNELS[service], json={"message": message}
        )
        return (
            jsonify({"status": "Notification sent", "response": response.json()}),
            200,
        )
    except requests.RequestException as e:
        return jsonify({"error": f"Failed to send notification: {str(e)}"}), 500


@app.route("/broadcast", methods=["POST"])
def broadcast_notification():
    data = request.json
    message = data.get("message")

    if not message:
        return jsonify({"error": "Missing message"}), 400

    results = {}
    for service, url in NOTIFICATION_CHANNELS.items():
        try:
            response = requests.post(url, json={"message": message})
            results[service] = response.json()
        except requests.RequestException as e:
            results[service] = f"Failed: {str(e)}"

    return jsonify({"status": "Broadcast complete", "results": results}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8010)
