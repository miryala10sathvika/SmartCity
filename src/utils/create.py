import requests


def check_cse_exists():
    """Check if the base CSE (in-name) exists"""
    url = "http://127.0.0.1:8080/~/in-cse/in-name/"
    headers = {"X-M2M-Origin": "admin:admin", "Accept": "application/json"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return True
    else:
        print(f"Failed to find base CSE. Status code: {response.status_code}")
        print("Response:", response.text)
        return False


def create_ae():
    """Create an Application Entity (AE)"""
    if not check_cse_exists():
        return

    url = "http://127.0.0.1:8080/~/in-cse/in-name/"
    headers = {
        "X-M2M-Origin": "admin:admin",
        "Content-Type": "application/json;ty=2",  # Use ty=2 for AE
    }
    payload = {"m2m:ae": {"rn": "SensorData", "api": "myAPI", "rr": True}}

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 201:
        print("Application Entity created successfully.")
        return response.json()["m2m:ae"][
            "ri"
        ]  # Return the resource ID of the created AE
    else:
        print(
            f"Failed to create Application Entity. Status code: {response.status_code}"
        )
        print("Response:", response.text)
        return None


def create_container(ae_id):
    """Create a container inside the specified Application Entity (AE)"""
    if not ae_id:
        print("No Application Entity ID provided. Skipping container creation.")
        return

    url = f"http://127.0.0.1:8080/~/in-cse/in-name/{ae_id}"
    headers = {
        "X-M2M-Origin": "admin:admin",
        "Content-Type": "application/json;ty=3",  # Use ty=3 for Container
    }
    payload = {"m2m:cnt": {"rn": "data"}}

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 201:
        print("Container created successfully inside Application Entity.")
    else:
        print(f"Failed to create Container. Status code: {response.status_code}")
        print("Response:", response.text)


if __name__ == "__main__":
    ae_id = create_ae()
    if not ae_id:
        create_container("SensorData")
    else:
        create_container(ae_id)
