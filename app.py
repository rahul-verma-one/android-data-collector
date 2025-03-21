import subprocess
import csv
import os
import time
from datetime import datetime
import tkinter as tk
from tkinter import messagebox


class DataCollectorUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Data Collector")
        self.root.geometry("400x300")
        self.app_packages = []
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

            self.action_button = tk.Button(self.root, text="Execute", command=self.on_execute_click)
            self.action_button.pack(pady=5)

            self.refresh_button = tk.Button(self.root, text="Refresh", command=self.on_refresh_click)
            self.refresh_button.pack(pady=5)

        except IndexError as e:
            messagebox.showerror("Error", "No app packages found. Please connect a device and try again.")
            self.root.destroy()
            return


    def on_execute_click(self):
        package = self.get_package_name()
        # TODO: Call further Method
        collector_app = DataCollectorApp(package)
        collector_app.collect_performance_data()
        

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

        return sorted_process_names



class DataCollectorApp:
    def __init__(self, package_name : str):
        self.app_package = package_name



    def list_all_processes(self, should_print_pid : bool = False):
        """
        List all the processes running on the device along with their PIDs
        """
        sorted_process_names = []
        try:
            process_raw = subprocess.run(['adb', 'shell', 'ps'], capture_output=True, text=True)
            process_list = process_raw.stdout.splitlines()
            
            # Extract the process names (assuming the process name is the last field)
            process_names = set()
            for line in process_list[1:] :  # Skip the header line
                fields = line.split()
                if fields:
                    process_name = fields[-1]  # Process name is the last field
                    if process_name.startswith('com.'):
                        process_names.add(process_name)
            
            # Sort the process names
            sorted_process_names = sorted(process_names)

            # Print the distinct process names in a prettified format
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



    def find_pid(self, package_name : str):
        """ 
        To find the PID of the app package
        adb shell pidof <Package Name>
        """
        pid = None
        try:
            pid_raw = subprocess.run(['adb', 'shell', 'pidof', package_name], capture_output=True, text=True)
            pid_list = [line for line in pid_raw.stdout.splitlines()]
            pid = pid_list[0]
        
        except Exception as e:
            print(f"Error: An error occurred: {e}")
        
        return pid
    


    def runner(self):
        #self.list_all_processes(False)
        self.collect_performance_data(self.app_package)



    def collect_performance_data(self, package_name) -> None:
        """
        The actual method that collects performance data
        """
        pid = self.find_pid(package_name)
        if pid is None:
            print(f"Error: The PID for {package_name} was not found.")
            return
        
        for i in range(4):
            output = self.collect_cpu_ram_data_pid(pid)
            filtered_output = [line for line in output.stdout.splitlines()]
            #print(filtered_output)
            count = 0
            print("+"*20, f"Iteration {i}th", "+"*20)
            for j in filtered_output:
                print("="*40)
                print(f"Output[{count}] :::: {j}")
                count += 1
                fields = j.split()                
                print(fields)
                print(F"Length of fields :: {len(fields)}")
                print("="*40)

        # Next


    def collect_cpu_ram_data_pid(self, pid : str):
        output = []
        try:
            #output = subprocess.run(['adb', 'shell', 'top', '-n', str(num_rows), '-d', str(refresh_interval), '-b'], capture_output=True, text=True)
            #output = subprocess.run(['adb', 'shell', 'top', '-n', str(num_rows), '-b'], capture_output=True, text=True)
            
            #output = subprocess.run(['adb', 'shell', 'top', '-p', '17588', '-b'], capture_output=True, text=True)
            output = subprocess.run(['adb', 'shell', 'top', '-n', '1' ,'-p', str(pid), '-b'], capture_output=True, text=True)
            
            #filtered_output = [line for line in output.stdout.splitlines() if self.app_package in line]
            filtered_output = [line for line in output.stdout.splitlines()]
            
            #print("Raw Output:\n", output)
            #print("Filtered Output:\n", filtered_output)
            #print(filtered_output)

            """
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
                writer.writerows(rows)"
            """

        except Exception as e:
            print(f"Error: An error occurred: {e}")
            #messagebox.showerror("Error", f"An error occurred: {e}")

        return output


if __name__ == "__main__":
    #dataUI = DataCollectorUI()
    #app = DataCollectorApp("com.facebook.katana")
    app = DataCollectorApp("com.google.android.contacts")
    app.runner()

   