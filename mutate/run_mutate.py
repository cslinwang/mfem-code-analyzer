
import argparse
import subprocess
import os
import time

# Path to the script to be monitored
script_path = '/root/mfem-code-analyzer/mutate/run_mutate_script.py'

# issue_name parameter

# Monitoring interval in seconds
monitor_interval = 600  # 10 minutes

# Subprocess variable
process = None
# 创建解析器
parser = argparse.ArgumentParser(description='Run tests for specified files.')
# 添加一个参数，可以传入零个或多个值，设定默认值
parser.add_argument('filenames', nargs='*', default=['issue1230'],
                    help='List of file names to run tests on')

args = parser.parse_args()

# 解析参数
args = parser.parse_args()

issue_name = args.filenames[0]
import psutil

cpu_usage = psutil.cpu_percent(interval=1)
print(f"Current CPU usage is: {cpu_usage}%")

while True:
    # If the process does not exist or has finished
    if process is None or process.poll() is not None:
        # Start the script
        process = subprocess.Popen(['python3', script_path, issue_name],
                                   stdout=None,
                                   stderr=None)
        print("Start the script: " + script_path)
    else:
        # Get the last modified time of the log file
        last_modified = os.path.getmtime(
            '/root/mfem-code-analyzer/mutate/log.log')

        # Wait for the specified monitoring interval
        time.sleep(monitor_interval)

        # Check if the file has been modified during the interval
        if last_modified == os.path.getmtime('/root/mfem-code-analyzer/mutate/log.log'):
            # If the file was not modified, terminate the current process
            process.terminate()
            print("Stuck detected, terminating and restarting the script")
            process = None
        else:
            print("Script is running normally")
