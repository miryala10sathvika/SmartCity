from locust import HttpUser, TaskSet, task, between, LoadTestShape, events
import random
import time
import threading
from collections import OrderedDict

# Global variable to track the current upper limit of the randint range
current_upper_limit = 10
stop_requests = False  # Global flag to control stopping requests
failure_count = 0  # Track the number of failures
stopping_time = 8  # Initial stopping time

# Function to update the upper limit and toggle request flag every 15 seconds
def update_upper_limit():
    global current_upper_limit, stop_requests, stopping_time
    while True:
        time.sleep(15)
        stop_requests = True  # Stop sending requests
        time.sleep(stopping_time)
        stop_requests = False  # Resume sending requests
        current_upper_limit += 10

# Start the thread to update the upper limit and control request flow
threading.Thread(target=update_upper_limit, daemon=True).start()

# Function to adjust stopping time based on failure count and time
def adjust_stopping_time():
    global stopping_time, failure_count
    while True:
        time.sleep(60)
        if stopping_time > 8:
            stopping_time -= 1
            print(f"Decreasing stopping time. New stopping time: {stopping_time} seconds")  

threading.Thread(target=adjust_stopping_time, daemon=True).start()

class LRUCache:
    def __init__(self, capacity: int):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key: str):
        if key not in self.cache:
            return None
        value = self.cache.pop(key)
        self.cache[key] = value
        return value

    def put(self, key: str, value: any):
        if key in self.cache:
            self.cache.pop(key)
        elif len(self.cache) >= self.capacity:
            self.cache.popitem(last=False)
        self.cache[key] = value

cache = LRUCache(50)  # Cache with 20 slots

class UserBehavior(TaskSet):

    @task
    def get_sensor_data(self):
        global current_upper_limit, stop_requests, failure_count, stopping_time
        if stop_requests:
            return  # Skip sending requests if the flag is set

        id = str(random.randint(1, current_upper_limit))
        
        # Check the cache first
        cached_data = cache.get(id)
        if cached_data is not None:
            return cached_data

        response = self.client.get(f"/get_data/{id}")
        if response.status_code == 200:
            data = response.json()
            # Store the received data in the cache
            cache.put(id, data)
            return data
        else:
            failure_count += 1
            if failure_count > 15:
                stopping_time += 2
                print(f"More than 15 failures, increasing stopping time to {stopping_time} seconds")
                failure_count = 0

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)
    host = "http://localhost:8004"  # Change this if your Flask app is hosted elsewhere

class StepLoadShape(LoadTestShape):
    """
    A step load shape
    """
    step_time = 30  # duration of each step in seconds
    step_users = 10  # number of users to add each step
    spawn_rate = 10  # number of users to spawn per second
    time_limit = 1200  # total time limit for the test in seconds

    def tick(self):
        run_time = self.get_run_time()

        if self.time_limit and run_time > self.time_limit:
            return None

        current_step = run_time // self.step_time + 1
        return (current_step * self.step_users, self.spawn_rate)

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    environment.runner.shape_class = StepLoadShape()

if __name__ == "__main__":
    import locust
    locust.run_single_user(WebsiteUser)
