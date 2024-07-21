import pandas as pd
import matplotlib.pyplot as plt

def plot_cpu_utilization(times, cpu_utilizations):
    plt.figure(figsize=(10, 5))
    plt.plot(times, cpu_utilizations, marker='o')
    plt.xlabel('Time')
    plt.ylabel('CPU Utilization (%)')
    plt.title('CPU Utilization Over Time')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def read_and_plot_csv(file_path):
    # Read the CSV file
    data = pd.read_csv(file_path)

    # Convert the 'Timestamp' column to datetime
    data['Timestamp'] = pd.to_datetime(data['Timestamp'])

    # Extract the columns for plotting
    times = data['Timestamp']
    cpu_utilizations = data['CPU Utilization']

    # Plot the data
    plot_cpu_utilization(times, cpu_utilizations)

if __name__ == "__main__":
    file_path = 'water_cpu_utilization.csv'  # Replace with your CSV file path
    read_and_plot_csv(file_path)
