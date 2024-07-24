import subprocess
import time
import sys
import os


def run_script(script_name):
    return subprocess.Popen([sys.executable, script_name])


def main():
    services = [
        "services/sensors/air/service.py",
        "services/sensors/water/service.py",
        "services/sensors/solar/service.py",
        "services/sensors/crowd/service.py",
        "services/sensors/room/service.py",
    ]

    processes = []

    # Start all service scripts
    for service in services:
        process = run_script(service)
        processes.append(process)
        print(f"Started {service}")
        time.sleep(2)

    # Start the main server
    main_server = run_script("services/sensors/server.py")
    processes.append(main_server)
    print("Started main_server/service.py")

    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Handle Ctrl+C to stop all processes
        print("\nStopping all services...")
        for process in processes:
            process.terminate()

        # Wait for all processes to finish
        for process in processes:
            process.wait()

        print("All services stopped.")


if __name__ == "__main__":
    main()
