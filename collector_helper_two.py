import subprocess
import os
import time
import csv
from datetime import datetime

class DataCollectorApp:
    def __init__(self, process_name):
        self.process_name = process_name
        print(f"Initializing Data Collection for process: {self.process_name}")
    
    def capture_metrics(self, interval=1, duration=60):
        try:
            output_dir = 'output'
            os.makedirs(output_dir, exist_ok=True)
            csv_file = os.path.join(output_dir, 'metrics.csv')
            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Timestamp', 'CPU Usage', 'Memory Usage', 'Network Usage', 'Battery Usage', 'GPU Usage'])
                start_time = time.time()

                while time.time() - start_time < duration:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    cpu_output = subprocess.run(['adb', 'shell', 'top', '-n', '1', '-b'], capture_output=True, text=True)
                    mem_output = subprocess.run(['adb', 'shell', 'dumpsys', 'meminfo'], capture_output=True, text=True)
                    cpu_usage = self.extract_cpu_usage(cpu_output.stdout)
                    mem_usage = self.extract_mem_usage(mem_output.stdout)
                    
                    #mem_output = subprocess.run(['adb', 'shell', 'dumpsys', 'meminfo', self.process_name], capture_output=True, text=True)

                    print(cpu_usage)
                    print(mem_usage)
                    print("="*30)
                    
                    """
                    # Capture Network usage
                    net_output = subprocess.run(['adb', 'shell', 'dumpsys', 'netstats'], capture_output=True, text=True)
                    net_usage = self.extract_net_usage(net_output.stdout)

                    # Capture Battery usage
                    battery_output = subprocess.run(['adb', 'shell', 'dumpsys', 'batterystats', self.process_name], capture_output=True, text=True)
                    battery_usage = self.extract_battery_usage(battery_output.stdout)

                    # Capture GPU usage
                    gpu_output = subprocess.run(['adb', 'shell', 'dumpsys', 'gfxinfo', self.process_name], capture_output=True, text=True)
                    gpu_usage = self.extract_gpu_usage(gpu_output.stdout)
                    
                    """

                    #writer.writerow([timestamp, cpu_usage, mem_usage, net_usage, battery_usage, gpu_usage])
                    writer.writerow([timestamp, mem_usage])
                    time.sleep(interval)

        except Exception as e:
            print(f"Error: An error occurred: {e}")
            # messagebox.showerror("Error", f"An error occurred: {e}")


    def extract_cpu_usage(self, output):
        # Extract relevant CPU usage information for the specific process from the output
        for line in output.splitlines():
            if self.process_name in line:
                fields = line.split()
                cpu_params = []
                cpu_params.append(fields[0]) # PID
                cpu_params.append(fields[1]) # User
                cpu_params.append(fields[4]) # VSize i.e Virtual Memory Size
                cpu_params.append(fields[5]) # RSS i.e Resident Memory Size
                cpu_params.append(fields[6]) # SHR i.e Shared Memory Size
                cpu_params.append(fields[7]) # S i.e Process State R-Running, S-Sleeping, D-Uninterruptible Sleep, Z-Zombie, T-Traced or Stopped
                cpu_params.append(fields[8]) # %CPU
                cpu_params.append(fields[9]) # %MEM
                return cpu_params  
        return "N/A"


    def extract_mem_usage(self, output):
        for line in output.splitlines():
            if self.process_name in line:
                fields = line.split()
                return fields[0]  # fields[0] has the Actual memory usage in KB
        return "N/A"


    def extract_net_usage(self, output):
        uid = self.get_uid_for_process(self.process_name)
        if uid == "N/A":
            return "N/A"
        
        for line in output.splitlines():
            if f"uid={uid}" in line:
                fields = line.split()
                rx_bytes = fields[1]  # Adjust based on the actual output format
                tx_bytes = fields[3]  # Adjust based on the actual output format
                return f"RX: {rx_bytes} bytes, TX: {tx_bytes} bytes"
        return "N/A"


    def extract_battery_usage(self, output):
        # Extract relevant Battery usage information for the specific process from the output
        for line in output.splitlines():
            if self.process_name in line:
                fields = line.split()
                return fields[1]  # Adjust based on the actual output format
        return "N/A"


    def extract_gpu_usage(self, output):
        # Extract relevant GPU usage information for the specific process from the output
        # This is a placeholder implementation; you need to parse the output as required
        return "N/A"


    def get_uid_for_process(self, process_name):
        output = subprocess.run(['adb', 'shell', 'ps'], capture_output=True, text=True)
        for line in output.stdout.splitlines():
            if process_name in line:
                fields = line.split()
                return fields[0]  # Assuming UID is the first field
        return "N/A"


if __name__ == "__main__":
    process_name = "com.facebook.katana"  # Replace with the actual process name
    app = DataCollectorApp(process_name)
    app.capture_metrics(interval=1, duration=10)  # Capture metrics every second for 60 seconds



"""
Bash -> adb shell top | grep com.facebook.
PowerShell -> adb shell top | Select-String 'com.facebook.'



"""