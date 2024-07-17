import requests

def delete_subscription(subscription_name):
    """This function deletes a subscription with the given name."""
    baseurl = f"http://127.0.0.1:8080/~/in-cse/in-name/SensorData/data/"
    headers = {
        "X-M2M-Origin": "admin:admin",
        "Content-Type": "application/xml"
    }
    response = requests.delete(baseurl, headers=headers)
    if response.status_code == 200:
        print(f"Subscription {subscription_name} deleted successfully.")
    else:
        print(f"Failed to delete subscription {subscription_name}. Status code: {response.status_code}")
        print(f"Response: {response.text}")

if __name__ == "__main__":
    subscription_name = "SensorDataSubscription"
    delete_subscription(subscription_name)
