import psutil
import time
import matplotlib.pyplot as plt
from datetime import datetime

def find_java_process(cmd_part):
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'java' in proc.info['name'] and cmd_part in ' '.join(proc.info['cmdline']):
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return None

def monitor_cpu_utilization(proc, interval, duration):
    times = []
    cpu_utilizations = []
    
    end_time = time.time() + duration
    while time.time() < end_time:
        times.append(datetime.now())
        cpu_utilizations.append(proc.cpu_percent(interval=interval))
    
    return times, cpu_utilizations

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

if __name__ == "__main__":
    cmd_part = 'java -jar -ea -Declipse.ignoreApp=true -Dosgi.clean=true -Ddebug=true plugins/org.eclipse.equinox.launcher_1.3.0.v20140415-2008.jar -console -noExit'
    
    java_process = find_java_process(cmd_part)
    
    if java_process:
        print(f"Found Java process: PID={java_process.pid}, Name={java_process.name()}")
        duration = 1200  # Monitor for 20 minutes
        times, cpu_utilizations = monitor_cpu_utilization(java_process, 30, duration)
        plot_cpu_utilization(times, cpu_utilizations)
    else:
        print("Java process not found.")