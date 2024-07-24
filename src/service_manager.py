import os
import multiprocessing
import time
from flask import Flask, render_template, jsonify, request
import importlib.util

app = Flask(__name__)

running_processes = {}


def get_services():
    services_dir = "services"
    services = {}
    for item in os.listdir(services_dir):
        item_path = os.path.join(services_dir, item)
        if os.path.isdir(item_path):
            if item == "sensors":
                services["sensors"] = [
                    d
                    for d in os.listdir(item_path)
                    if os.path.isdir(os.path.join(item_path, d))
                ]
            elif os.path.exists(os.path.join(item_path, "service.py")):
                services[item] = None
    return services


@app.route("/")
def index():
    services = get_services()
    return render_template("index.html", services=services)


@app.route("/api/services")
def api_services():
    services = get_services()
    status = {}
    for service, subservices in services.items():
        if subservices:
            status[service] = {
                subservice: f"{service}/{subservice}" in running_processes
                for subservice in subservices
            }
        else:
            status[service] = service in running_processes
    return jsonify(status)


def run_service(service_path):
    spec = importlib.util.spec_from_file_location(
        "service", f"services/{service_path}/service.py"
    )
    service_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(service_module)
    if hasattr(service_module, "run"):
        service_module.run()
    else:
        print(f"Warning: {service_path} does not have a 'run' function")


def start_service(service_path):
    if service_path not in running_processes:
        process = multiprocessing.Process(target=run_service, args=(service_path,))
        process.start()
        running_processes[service_path] = process
        return True
    return False


def stop_service(service_path):
    if service_path in running_processes:
        process = running_processes[service_path]
        process.terminate()
        process.join(timeout=5)
        if process.is_alive():
            process.kill()
            print(f"Killed {service_path}")
        del running_processes[service_path]
        return True
    return False


@app.route("/api/toggle/<path:service_path>", methods=["POST"])
def toggle_service(service_path):
    if service_path in running_processes:
        if stop_service(service_path):
            return jsonify({"status": "stopped"})
        else:
            return (
                jsonify(
                    {"status": "error", "message": f"Failed to stop {service_path}"}
                ),
                500,
            )
    else:
        if start_service(service_path):
            return jsonify({"status": "started"})
        else:
            return (
                jsonify(
                    {"status": "error", "message": f"Failed to start {service_path}"}
                ),
                500,
            )


@app.route("/api/toggle_all_sensors", methods=["POST"])
def toggle_all_sensors():
    services = get_services()
    sensor_services = services.get("sensors", [])
    action = request.json.get("action")

    if action == "start":
        for sensor in sensor_services:
            start_service(f"sensors/{sensor}")
        return jsonify({"status": "started all sensors"})
    elif action == "stop":
        for sensor in sensor_services:
            stop_service(f"sensors/{sensor}")
        return jsonify({"status": "stopped all sensors"})
    else:
        return jsonify({"status": "error", "message": "Invalid action"}), 400


if __name__ == "__main__":
    multiprocessing.freeze_support()  # Needed for Windows
    app.run(debug=True, port=8013, use_reloader=False)
