from locust import HttpUser, TaskSet, task, between, LoadTestShape, events
import random
import time
import threading

# Global variable to track the current upper limit of the randint range
current_upper_limit = 10

# Function to update the upper limit every 15 seconds
def update_upper_limit():
    global current_upper_limit
    while True:
        time.sleep(15)
        current_upper_limit += 10

# Start the thread to update the upper limit
threading.Thread(target=update_upper_limit, daemon=True).start()

class UserBehavior(TaskSet):

    @task
    def get_sensor_data(self):
        global current_upper_limit
        id = str(random.randint(1, current_upper_limit))
        self.client.get(f"/get_data/{id}")

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)
    host = "http://localhost:8002"  # Change this if your Flask app is hosted elsewhere

class StepLoadShape(LoadTestShape):
    """
    A step load shape
    """
    step_time = 30  # duration of each step in seconds
    step_users = 10  # number of users to add each step
    spawn_rate = 10  # number of users to spawn per second
    time_limit = 1200  # total time limit for the test in seconds (10 minutes)

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
