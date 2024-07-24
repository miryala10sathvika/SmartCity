from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/notification/air', methods=['POST'])
def forward_air_notification():
    return forward_notification('http://localhost:8001/notification')

@app.route('/notification/water', methods=['POST'])
def forward_water_notification():
    return forward_notification('http://localhost:8002/notification')

@app.route('/notification/solar', methods=['POST'])
def forward_solar_notification():
    return forward_notification('http://localhost:8003/notification')

@app.route('/notification/crowd', methods=['POST'])
def forward_crowd_notification():
    return forward_notification('http://localhost:8004/notification')

@app.route('/notification/room', methods=['POST'])
def forward_room_notification():
    return forward_notification('http://localhost:8005/notification')

def forward_notification(service_url):
    try:
        response = requests.post(service_url, data=request.data, headers=request.headers)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
