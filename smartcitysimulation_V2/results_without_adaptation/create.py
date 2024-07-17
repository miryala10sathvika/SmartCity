import requests

def create_ae():
    """Create an Application Entity (AE)"""
    url = "http://127.0.0.1:8080/~/in-cse/in-name/SensorData"
    headers = {
        "X-M2M-Origin": "admin:admin",
        "Content-Type": "application/json;ty=3"
    }
    payload = {
    "m2m:cnt":{
        "rn": "data"
    }
}
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 201:
        print("Application Entity created successfully.")
    else:
        print(f"Failed to create Application Entity. Status code: {response.status_code}")
        print("Response:", response.text)

if __name__ == "__main__":
    create_ae()
