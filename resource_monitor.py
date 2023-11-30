import subprocess
import psutil
import os
import time

def log_resource_usage(script_path):
    """
    Logs the CPU and memory usage of a Python script, accounting for multiple threads.

    Args:
    script_path (str): The path to the Python script to monitor.

    Returns:
    str: A log of the CPU and memory usage.
    """
    # Use the appropriate command to start the Python script based on the operating system
    if os.name == 'nt':  # Windows
        command = ['python', script_path]
    else:  # Unix/Linux
        command = ['python3', script_path]

    # Start the Python script as a subprocess
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Get process id
    pid = process.pid

    # Create a psutil Process object for the subprocess
    py_process = psutil.Process(pid)

    # Initialize variables to store maximum CPU and memory usage
    max_cpu_usage = 0
    max_memory_usage = 0

    # Monitor the CPU and memory usage of the process, including its children
    while True:
        try:
            # Get the children of the process (if any)
            children = py_process.children(recursive=True)
            all_processes = [py_process] + children

            # Initialize current CPU and memory usage
            current_cpu_usage = 0
            current_memory_usage = 0

            # Aggregate the resource usage of the main process and its children
            for proc in all_processes:
                current_cpu_usage += proc.cpu_percent() / psutil.cpu_count()
                current_memory_usage += proc.memory_info()[0] / 2. ** 30  # Memory usage in GB

            # Update max values if current usage is greater
            max_cpu_usage = max(max_cpu_usage, current_cpu_usage)
            max_memory_usage = max(max_memory_usage, current_memory_usage)

            # Wait for a short period to prevent excessive resource usage in the monitoring
            time.sleep(0.1)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Process has finished or cannot access process information, break the loop
            break

    return f"Max CPU Usage: {max_cpu_usage}%\nMax Memory Usage: {max_memory_usage:.2f} GB"

# Note: Replace 'path_to_script.py' with the actual path of the Python script you want to monitor.
