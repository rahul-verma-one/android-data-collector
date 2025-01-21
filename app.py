# Run this app to start the performacance test
import subprocess
import csv
import os
import time
from datetime import datetime
import tkinter as tk
from tkinter import messagebox


class DataCollectorApp:
    def __init__(self):
        print("Initializing Data Collection")
        self.app_package = "com.instagram.android"
    
    def collect_performance_data(self):
        num_rows = 2
        refresh_interval = 3
        try:

            # Execute adb shell top command to retrieve process information
            output = subprocess.run(['adb', 'shell', 'top', '-n', str(num_rows), '-d', str(refresh_interval), '-b'], capture_output=True, text=True)
            
            # Filter the output to select lines corresponding to the specified app package
            #filtered_output = [line for line in output.stdout.splitlines() if self.app_package in line]
            
            # Filter the output to select all lines
            filtered_output = [line for line in output.stdout.splitlines()]
            
            # Print the raw output for debugging purposes
            #print("Raw Output:\n", output.stdout)
            
            # Print the filtered output for debugging purposes
            print("Filtered Output:\n", filtered_output)

            # Parse the output and extract relevant information
            rows = []
            for line in filtered_output:
                fields = line.split()
                if len(fields) >= 12:  # Adjust the condition based on your top output format
                    pid = fields[0]
                    user = fields[1]
                    priority = fields[2]
                    nice = fields[3]
                    vsize = fields[4]
                    rss = fields[5]
                    pcpu = fields[8].replace('%', '')  # CPU usage
                    pmem = fields[9].replace('%', '')  # Memory usage
                    time = fields[10]
                    command = ' '.join(fields[11:])  # Command might contain spaces
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    rows.append([timestamp, pid, user, priority, nice, vsize, rss, pcpu, pmem, time, command])

            # Print the rows for debugging purposes
            print("Parsed Rows:\n", rows)
            
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)

            # Write the collected data to a CSV file
            output_file = os.path.join(output_dir, "CollectedData.csv")
            with open(output_file, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Timestamp', 'PID', 'User', 'Priority', 'Nice', 'VSize', 'RSS', 'CPU Usage', 'Memory Usage', 'Time', 'Command'])
                writer.writerows(rows)

        except Exception as e:
            print(f"Error: An error occurred: {e}")
            #messagebox.showerror("Error", f"An error occurred: {e}")


    def collect_network_data(self):
        try:
            # Execute adb shell dumpsys netstats command to retrieve network information
            output = subprocess.run(['adb', 'shell', 'dumpsys', 'netstats'], capture_output=True, text=True)
            
            # Filter the output to select lines corresponding to the specified app package
            filtered_output = [line for line in output.stdout.splitlines() if self.app_package in line]
            
            # Print the raw output for debugging purposes
            print("Raw Output:\n", output.stdout)
            
            # Print the filtered output for debugging purposes
            print("Filtered Output:\n", filtered_output)

        except Exception as e:
            print(f"Error: An error occurred: {e}")
            #messagebox.showerror("Error", f"An error occurred: {e}")


    def collect_battery_data(self):
        try:
            # Execute adb shell dumpsys batterystats command to retrieve battery information
            output = subprocess.run(['adb', 'shell', 'dumpsys', 'batterystats'], capture_output=True, text=True)
            
            # Filter the output to select lines corresponding to the specified app package
            filtered_output = [line for line in output.stdout.splitlines() if self.app_package in line]
            
            # Print the raw output for debugging purposes
            print("Raw Output:\n", output.stdout)
            
            # Print the filtered output for debugging purposes
            print("Filtered Output:\n", filtered_output)

        except Exception as e:
            print(f"Error: An error occurred: {e}")
            #messagebox.showerror("Error", f"An error occurred: {e}")



    def list_all_processes(self):
        try:
            # Execute adb shell ps command to retrieve the list of all running processes
            output = subprocess.run(['adb', 'shell', 'ps'], capture_output=True, text=True)

            # Print the raw output for debugging purposes
            #print("Raw Output:\n", output.stdout)

            # Split the output into lines
            process_list = output.stdout.splitlines()
            # Extract the process names (assuming the process name is the last field)
            process_names = set()
            for line in process_list[1:]:  # Skip the header line
                fields = line.split()
                if fields:
                    process_name = fields[-1]  # Process name is the last field
                    if process_name.startswith('com.'):  # Include only processes that start with 'com.'
                        process_names.add(process_name)

            # Sort the process names
            sorted_process_names = sorted(process_names)

            # Print the distinct process names in a prettified format
            print("Distinct Process Names (starting with 'com.'):")
            for process_name in sorted_process_names:
                print(process_name)

        except Exception as e:
            print(f"Error: An error occurred: {e}")



    def capture_metrics(self, interval=1, duration=60):
        try:
            # Ensure the output directory exists
            output_dir = 'output'
            os.makedirs(output_dir, exist_ok=True)

            # Open the CSV file for appending
            csv_file = os.path.join(output_dir, 'metrics.csv')
            with open(csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                
                # Write the header row
                writer.writerow(['Timestamp', 'CPU Usage', 'Memory Usage', 'Network Usage', 'Battery Usage', 'GPU Usage'])

                start_time = time.time()
                while time.time() - start_time < duration:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    # Capture CPU usage
                    cpu_output = subprocess.run(['adb', 'shell', 'dumpsys', 'cpuinfo'], capture_output=True, text=True)
                    cpu_usage = self.extract_cpu_usage(cpu_output.stdout)

                    # Capture Memory (RAM) usage
                    mem_output = subprocess.run(['adb', 'shell', 'dumpsys', 'meminfo'], capture_output=True, text=True)
                    mem_usage = self.extract_mem_usage(mem_output.stdout)

                    # Capture Network usage
                    net_output = subprocess.run(['adb', 'shell', 'dumpsys', 'netstats'], capture_output=True, text=True)
                    net_usage = self.extract_net_usage(net_output.stdout)

                    # Capture Battery usage
                    battery_output = subprocess.run(['adb', 'shell', 'dumpsys', 'batterystats'], capture_output=True, text=True)
                    battery_usage = self.extract_battery_usage(battery_output.stdout)

                    # Capture GPU usage
                    gpu_output = subprocess.run(['adb', 'shell', 'dumpsys', 'gfxinfo'], capture_output=True, text=True)
                    gpu_usage = self.extract_gpu_usage(gpu_output.stdout)

                    # Write the captured data to the CSV file
                    writer.writerow([timestamp, cpu_usage, mem_usage, net_usage, battery_usage, gpu_usage])

                    # Wait for the specified interval
                    time.sleep(interval)

        except Exception as e:
            print(f"Error: An error occurred: {e}")
            # Uncomment the following line if you want to show a message box in a GUI application
            # messagebox.showerror("Error", f"An error occurred: {e}")

    def extract_cpu_usage(self, output):
        # Extract relevant CPU usage information from the output
        # This is a placeholder implementation; you need to parse the output as required
        return output.strip()

    def extract_mem_usage(self, output):
        # Extract relevant Memory usage information from the output
        # This is a placeholder implementation; you need to parse the output as required
        return output.strip()

    def extract_net_usage(self, output):
        # Extract relevant Network usage information from the output
        # This is a placeholder implementation; you need to parse the output as required
        return output.strip()

    def extract_battery_usage(self, output):
        # Extract relevant Battery usage information from the output
        # This is a placeholder implementation; you need to parse the output as required
        return output.strip()

    def extract_gpu_usage(self, output):
        # Extract relevant GPU usage information from the output
        # This is a placeholder implementation; you need to parse the output as required
        return output.strip()



if __name__ == "__main__":
    app = DataCollectorApp()
    #app.collect_performance_data()
    app.list_all_processes()
    #app.list_all_processes_distinct()





'''
Igonre these further lines.


For Network profiling 

adb shell dumpsys netstats > network_usage.txt

cat network_usage.txt | grep -E 'iface|uid|rxBytes|txBytes'



For Battery profiling 

adb shell dumpsys batterystats > battery_usage.txt

cat battery_usage.txt | grep -E 'Uid|Foreground|Wakelock|Network|Sensor|GPS|Wifi|Bluetooth|Camera|Flashlight|Screen|Phone|Idle|Over-counted|Unaccounted'



For Memory profiling 

adb shell dumpsys meminfo > memory_usage.txt

cat memory_usage.txt | grep -E 'Native|Dalvik|TOTAL'



For CPU profiling 

adb shell dumpsys cpuinfo > cpu_usage.txt

cat cpu_usage.txt | grep -E 'Load|CPU|Proc|User|System|IRQ|SoftIRQ|Idle|IOWait|Irq|SoftIrq|Steal|Guest|GuestNice'



For Frame profiling 

adb shell dumpsys gfxinfo > frame_usage.txt

cat frame_usage.txt | grep -E 'Total|Janky|Missed|High|50th|90th|95th|99th|Number|Histogram'



For App profiling 

adb shell dumpsys package > app_usage.txt

cat app_usage.txt | grep -E 'Package|User|Version|Code|Data|Cache|Size|Data|Code|Cache|UID|Flags|Permissions|Requested|Install|Uninstall|Shared|Runtime|Stopped|Not|Enabled|Installed|Hidden



For Process profiling 

adb shell dumpsys activity processes > process_usage.txt

cat process_usage.txt | grep -E 'Process|PID|UID|User|State|OOM|Adj|Proc|PSS|Shmem



For Sensor profiling 

adb shell dumpsys sensorservice > sensor_usage.txt

cat sensor_usage.txt | grep -E 'Sensor|Type|Vendor|Version|Max|Resolution|Power|Min|Fifo|Max|Wake|Reporting|Mode|Delay|Max|Batch|Fifo|Reserved|Flags|Wake|Up|Events|Batch|Timeout



For Location profiling 

adb shell dumpsys location > location_usage.txt

cat location_usage.txt | grep -E 'Location|Provider|Status|Power|Accuracy|Latitude|Longitude|Altitude|Speed|Bearing|Extras|Elapsed|Real|Time|Last|Status|Enabled|Request|Interval|Fastest|Min|Update|Distance|Accuracy|Power|Settings|Provider|Status|Power|Accuracy|Latitude|Longitude|Altitude|Speed|Bearing|Extras|Elapsed|Real|Time|Last|Status|Enabled|Request|Interval|Fastest|Min|Update|Distance|Accuracy|Power|Settings



For Display profiling 

adb shell dumpsys display > display_usage.txt



For Alarm profiling 

adb shell dumpsys alarm > alarm_usage.txt



For Notification profiling 

adb shell dumpsys notification > notification_usage.txt


'''