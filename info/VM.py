import time
import subprocess
import os
import psutil
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient

# Configuration parameters
CPU_HIGH_THRESHOLD = 80.0  # Percentage to trigger scale-up
CPU_LOW_THRESHOLD = 30.0   # Percentage to trigger scale-down
POLL_INTERVAL = 10         # Time (seconds) between checks

def start_instance():
    """Logic to spin up a new VM instance or worker process."""
    print("Scaling UP: High CPU detected. Starting new instance...")
    # Example: run a shell command to start an instance
    # subprocess.run(["gcloud", "compute", "instances", "start", "INSTANCE_NAME"])

def stop_instance():
    """Logic to shut down a VM instance or worker process."""
    print("Scaling DOWN: Low CPU detected. Shutting down an instance...")
    # Example: run a shell command to stop an instance
    # subprocess.run(["gcloud", "compute", "instances", "stop", "INSTANCE_NAME"])

def monitor_and_scale():
    print("Starting CPU monitor for auto-scaling...")
    try:
        while True:
            # Get the current system-wide CPU utilization over the interval
            cpu_usage = psutil.cpu_percent(interval=1)
            print(f"Current CPU Usage: {cpu_usage}%")
            
            if cpu_usage > CPU_HIGH_THRESHOLD:
                start_instance()
            elif cpu_usage < CPU_LOW_THRESHOLD:
                stop_instance()
                
            time.sleep(POLL_INTERVAL)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")



if __name__ == "__main__":
    monitor_and_scale()
