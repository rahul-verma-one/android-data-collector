import threading
import subprocess
import csv
import time
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

class DataCollectorUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Data Collector")
        self.root.geometry("400x400")
        self.app_packages = []
        self.interval_var = tk.IntVar()
        self.interval_var.set(1000)  # Default of 1000ms i.e. 1 sec
        self.create_widgets()
        self.root.mainloop()
        
    def create_widgets(self):
        try:
            self.app_packages = self.list_all_processes()
            self.dropdown_label = tk.Label(self.root, text="Select Option:")
            self.dropdown_label.pack(pady=5)

            self.selected_option = tk.StringVar(self.root)
            self.selected_option.set(self.app_packages[0])

            self.dropdown = tk.OptionMenu(self.root, self.selected_option, *self.app_packages)
            self.dropdown.pack(pady=5)

            self.refresh_button = tk.Button(self.root, text="Refresh", command=self.on_refresh_click)
            self.refresh_button.pack(pady=5)

            self.interval_label = tk.Label(self.root, text="Select Interval:")
            self.interval_label.pack(pady=5)
            
            self.radio_500ms = tk.Radiobutton(self.root, text="500 ms", variable=self.interval_var, value=500)
            self.radio_500ms.pack()
            
            self.radio_1000ms = tk.Radiobutton(self.root, text="1000 ms", variable=self.interval_var, value=1000)
            self.radio_1000ms.pack()

            self.start_button = tk.Button(self.root, text="Execute", command=self.on_execute_click)
            self.start_button.pack(pady=5)

            self.stop_button = tk.Button(self.root, text="Stop", command=self.on_stop_click)
            self.stop_button.pack(pady=5)

            self.close_button = tk.Button(self.root, text="Close", command=self.on_close_click)
            self.close_button.pack(pady=5)

        except IndexError as e:
            messagebox.showerror("Error", "No app packages found. Please connect a device and try again.")
            self.root.destroy()
            return


    def on_execute_click(self):
        package = self.get_package_name()
        interval = self.interval_var.get()
        
        self.collector_app = DataCollectorApp(package, interval)
        self.app_thread = threading.Thread(target=self.collector_app.run, daemon=True)
        self.app_thread.start()
        

    def on_stop_click(self):
        if hasattr(self, 'collector_app'):
            self.collector_app.set_run(False)


    def on_close_click(self):
        if hasattr(self, 'collector_app'):
            self.collector_app.set_run(False)
        self.root.destroy()  


    def on_refresh_click(self):
        self.app_packages = self.list_all_processes()
        self.selected_option.set(self.app_packages[0])
        self.dropdown['menu'].delete(0, 'end')
        for package in self.app_packages:
            self.dropdown['menu'].add_command(label=package, command=tk._setit(self.selected_option, package))


    def get_package_name(self):
        package_name = self.selected_option.get()
        print("The Package Name is: ", package_name)
        return package_name


    def list_all_processes(self):
        sorted_process_names = []
        try:
            output = subprocess.run(['adb', 'shell', 'ps'], capture_output=True, text=True)
            process_list = output.stdout.splitlines()
            process_names = set()
            for line in process_list[1:]:  # Skip the header line
                fields = line.split()
                if fields:
                    process_name = fields[-1]  # Process name is the last field
                    process_names.add(process_name)
                    #if process_name.startswith('com.'):  # Include only processes that start with 'com.'
                    #    process_names.add(process_name)
            sorted_process_names = sorted(process_names)
            #print("Distinct Process Names (starting with 'com.'):")
            #for process_name in sorted_process_names:
            #    print(process_name)

        except Exception as e:
            print(f"Error: An error occurred: {e}")

        return sorted_process_names


class DataCollectorApp:
    def __init__(self, package_name: str, time_interval: int = 1000):
        self.app_package = package_name
        self.interval_ms = time_interval / 1000  # Convert milliseconds to seconds
        self.can_run = True


    def set_run(self, can_run: bool):
        self.can_run = can_run


    def run(self):
        self.can_run = True
        self.collect_performance_data(self.app_package)
        

    def collect_performance_data(self, package_name) -> None:
        """
        The actual method that collects performance data
        """
        #self.list_all_processes(True)
        #return
        pid = self.find_pid(package_name)
        if pid is None:
            print(f"Error: The PID for {package_name} was not found.")
            return
        #print(f"Success: The PID for {package_name} is {pid}.")
        
        print("Following are the extreacted data")

        header = [  # For RAM
                    'Timestamp', 'RAM_Total_KB', 'RAM_Used_KB', 'RAM_Free_KB', 'RAM_Buffers_KB',
                    # For Swap
                    'Swap_Total_KB', 'Swap_Used_KB', 'Swap_Free_KB', 'Swap_Cached_KB',
                    # For CPU
                    'CPU_Total', 'CPU_User', 'CPU_System', 'CPU_Idle', 'CPU_Wait_IO', 'CPU_INTR_HW', 'CPU_INTR_SW',
                    # For App Usage
                    'PID', 'Priority', 'Virtual_Size_GB', 'RSS_Memory_MB','Shared_Memory_MB',
                    'App_State', 'CPU_Usage_Percent', 'Memory_Usage_Percent','Running_Time'
                  ]
        file_timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f"{package_name}_{file_timestamp}.csv"
        output_file = open(filename, 'w', newline='')
        file_writer = csv.writer(output_file)
        file_writer.writerow(header)
        print(f"Output will be saved to {filename}")

        while self.can_run:
            try:
                output = self.data_cpu_ram_with_pid(pid)
                filtered_output = [line for line in output.stdout.splitlines()]

                ram_filtered = filtered_output[1].split()
                swap_filtered = filtered_output[2].split()
                cpu_filtered = filtered_output[3].split()
                app_filtered = filtered_output[5].split()

                ram_usage =[]
                ram_usage.append(ram_filtered[1].rstrip('K')) 
                ram_usage.append(ram_filtered[3].rstrip('K'))
                ram_usage.append(ram_filtered[5].removesuffix('K'))
                ram_usage.append(ram_filtered[7].removesuffix('K'))

                swap_usage = []
                swap_usage.append(swap_filtered[1].removesuffix('K'))
                swap_usage.append(swap_filtered[3].removesuffix('K'))
                swap_usage.append(swap_filtered[5].removesuffix('K'))
                swap_usage.append(swap_filtered[7].removesuffix('K'))

                cpu_values = [(s.rstrip('%abcdefghijklmnopqrstuvwxyz')) for s in cpu_filtered]
                cpu_usage = []
                cpu_usage.append(cpu_values[0])
                cpu_usage.append(cpu_values[1])
                cpu_usage.append(cpu_values[3])
                cpu_usage.append(cpu_values[4])
                cpu_usage.append(cpu_values[5])
                cpu_usage.append(cpu_values[6])
                cpu_usage.append(cpu_values[7])

                app_usage = []
                app_usage.append(app_filtered[0])
                app_usage.append(app_filtered[2])
                app_usage.append(app_filtered[4].rstrip('G'))
                app_usage.append(app_filtered[5].rstrip('M'))
                app_usage.append(app_filtered[6].rstrip('M'))
                app_usage.append(app_filtered[7])
                app_usage.append(app_filtered[8])
                app_usage.append(app_filtered[9])
                app_usage.append(app_filtered[10])

                # print(f"RAM: {ram_usage}")
                # print(f"Swap: {swap_usage}")
                # print(f"CPU: {cpu_usage}")
                # print(f"App Metrics: {app_usage}")
                # print("+" * 30)

                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                one_record =[]
                one_record.append(timestamp)
                one_record.extend(ram_usage)
                one_record.extend(swap_usage)
                one_record.extend(cpu_usage)
                one_record.extend(app_usage)

                file_writer.writerow(one_record)
                print(f"Data collected at {timestamp}: {one_record}")
                time.sleep(self.interval_ms)
            
            except Exception as e:
                print("=" * 20)
                print(f"Error: An error occurred while collecting data: {e}")
                print("filetered_output: ", len(filtered_output))
                print("ram_usage_count: ", len(ram_usage))
                print("swap_usage_count: ", len(swap_usage))
                print("cpu_usage_count: ", len(cpu_usage))
                print("app_usage_count: ", len(app_usage))
                print("Continuing to next iteration...")
                print("=" * 20)
            #End of the Iteration
        
        print(f"Data collection completed. Output saved to {filename}")
        output_file.close()


    def list_all_processes(self, should_print_pid: bool = False):
        """
        List all the processes running on the device along with their PIDs
        """
        sorted_process_names = []
        try:
            process_raw = subprocess.run(
                ["adb", "shell", "ps"], capture_output=True, text=True
            )
            process_list = process_raw.stdout.splitlines()
            process_names = set()
            for line in process_list[1:]:  # Skip the header line
                fields = line.split()
                if fields:
                    process_name = fields[-1]  # Process name is the last field
                    if process_name.startswith("com."):
                        process_names.add(process_name)

            sorted_process_names = sorted(process_names)
            print("All Process Names (starting with 'com.'):")
            if should_print_pid:
                for process_name in sorted_process_names:
                    pid = self.find_pid(process_name)
                    print(f"{pid} ::::: {process_name}")
            else:
                for process_name in sorted_process_names:
                    print(f"{process_name}")

        except Exception as e:
            print(f"Error: An error occurred: {e}")


    def find_pid(self, package_name: str):
        """
        To find the PID of the app package
        adb shell pidof <Package Name>
        """
        pid = None
        try:
            pid_raw = subprocess.run(
                ["adb", "shell", "pidof", package_name], capture_output=True, text=True
            )
            pid_list = [line for line in pid_raw.stdout.splitlines()]
            pid = pid_list[0]

        except Exception as e:
            print(f"Error: An error occurred: {e}")

        return pid


    def data_cpu_ram_with_pid(self, pid: str):
        output = []
        try:
            # output = subprocess.run(['adb', 'shell', 'top', '-n', str(num_rows), '-d', str(refresh_interval), '-b'], capture_output=True, text=True)
            # output = subprocess.run(['adb', 'shell', 'top', '-n', str(num_rows), '-b'], capture_output=True, text=True)
            # output = subprocess.run(['adb', 'shell', 'top', '-p', '17588', '-b'], capture_output=True, text=True)
            output = subprocess.run(
                ["adb", "shell", "top", "-n", "1", "-p", str(pid), "-b"],
                capture_output=True,
                text=True,
            )
            filtered_output = [line for line in output.stdout.splitlines()]
            
        except Exception as e:
            print(f"Error: An error occurred: {e}")
            # messagebox.showerror("Error", f"An error occurred: {e}")
        return output


    def data_cpu_ram(self, package_name: str):
        """
        Collects CPU and RAM data for a given package using the 'top' command.
        Currently, it is not being used.
        """
        output = []
        try:
            result = subprocess.run(
                ['adb', 'shell', 'top', '-n', '1', '-b'],
                capture_output=True, text=True
            )
            #filtered_output = [line for line in output.stdout.splitlines()]
            for line in result.stdout.splitlines():
                if package_name in line:
                    fields = line.split()
                    if len(fields) >= 10:
                        return {
                            "PID": fields[0],
                            "CPU %": fields[8].replace('%', ''),
                            "Memory %": fields[9].replace('%', ''),
                            "Process Line": line
                        }
            return {"error": f"{package_name} not found in top output"}
        
        except Exception as e:
            return {"error": str(e)}



if __name__ == "__main__":
    app = DataCollectorUI()
