import os
import statistics
import time
from colorama import Fore, Style, init

RESULTS_PATH = "../../cupcarbon/results/"
AIR_SINK = "SINK_19.txt"

# Global variables to maintain state between function calls
previous_means = {}
previous_std_devs = {}


def check_data_drift():
    global previous_means, previous_std_devs

    try:
        with open(os.path.join(RESULTS_PATH, AIR_SINK), "r") as file:
            # Read all lines and get the last 5
            lines = file.readlines()
            last_5_lines = lines[-5:]

            # Extract values from the last 5 lines
            data = [list(map(float, line.strip().split())) for line in last_5_lines]

            # Separate timestamp and node data
            timestamps = [row[0] for row in data]
            node_data = [row[1:] for row in data]

            # Calculate statistics for each node
            num_nodes = len(node_data[0])
            for node in range(num_nodes):
                node_values = [row[node] for row in node_data]
                current_mean = statistics.mean(node_values)
                current_std_dev = statistics.stdev(node_values)

                if node in previous_means and node in previous_std_devs:
                    # Calculate the difference in means
                    mean_diff = abs(current_mean - previous_means[node])

                    # Determine the color based on the difference
                    if mean_diff < 0.1 * previous_std_devs[node]:
                        color = Fore.GREEN
                        message = "No significant drift"
                    elif mean_diff < 0.5 * previous_std_devs[node]:
                        color = Fore.YELLOW
                        message = "Slight drift detected"
                    else:
                        color = Fore.RED
                        message = "Significant drift detected"

                    print(f"Node {node}: {color}{message}{Style.RESET_ALL}")
                    print(
                        f"Current mean: {current_mean:.2f}, Previous mean: {previous_means[node]:.2f}"
                    )
                    print(
                        f"Current std dev: {current_std_dev:.2f}, Previous std dev: {previous_std_devs[node]:.2f}"
                    )
                else:
                    print(
                        Fore.BLUE
                        + f"Initial data collected for Node {node}"
                        + Style.RESET_ALL
                    )

                previous_means[node] = current_mean
                previous_std_devs[node] = current_std_dev

            print(f"Timestamp range: {timestamps[0]:.2f} - {timestamps[-1]:.2f}")
            print("-" * 50)

    except FileNotFoundError:
        print(
            Fore.RED
            + f"Error: File {AIR_SINK} not found in {RESULTS_PATH}"
            + Style.RESET_ALL
        )
    except ValueError:
        print(Fore.RED + "Error: Invalid data format in the file" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"An unexpected error occurred: {str(e)}" + Style.RESET_ALL)


def run_data_drift_monitor():
    init()  # Initialize colorama
    print("Starting data drift monitoring...")
    while True:
        check_data_drift()
        time.sleep(5)


if __name__ == "__main__":
    run_data_drift_monitor()
