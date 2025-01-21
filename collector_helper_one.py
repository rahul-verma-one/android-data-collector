import subprocess
import csv
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

class PerformanceDataCollectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Performance Data Collector")

        self.create_widgets()

    def create_widgets(self):
        # App package label and entry
        self.app_package_label = tk.Label(self.root, text="App Package:")
        self.app_package_label.pack(pady=5)
        self.app_package_entry = tk.Entry(self.root)
        self.app_package_entry.pack(pady=5)

        # Number of rows label and entry
        self.rows_label = tk.Label(self.root, text="Number of Rows:")
        self.rows_label.pack(pady=5)
        self.rows_entry = tk.Entry(self.root)
        self.rows_entry.pack(pady=5)

        # Refresh interval label and entry
        self.interval_label = tk.Label(self.root, text="Refresh Interval (seconds):")
        self.interval_label.pack(pady=5)
        self.interval_entry = tk.Entry(self.root)
        self.interval_entry.pack(pady=5)

        # Collect data button
        self.collect_button = tk.Button(self.root, text="Collect Data", command=self.collect_performance_data)
        self.collect_button.pack(pady=20)

    def collect_performance_data(self):
        app_package = self.app_package_entry.get()
        num_rows = self.rows_entry.get()
        refresh_interval = self.interval_entry.get()

        if not app_package or not num_rows.isdigit() or not refresh_interval.isdigit():
            messagebox.showerror("Error", "Please enter valid values for all fields.")
            return

        num_rows = int(num_rows)
        refresh_interval = int(refresh_interval)

        try:
            # Execute adb shell top command to retrieve process information
            output = subprocess.run(['adb', 'shell', 'top', '-n', str(num_rows), '-d', str(refresh_interval), '-b'], capture_output=True, text=True)

            # Filter the output to select lines corresponding to the specified app package
            filtered_output = [line for line in output.stdout.splitlines() if app_package in line]
            
            # Print the raw output for debugging purposes
            print("Raw Output:\n", output.stdout)
            
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

            # Write the collected data to a CSV file
            with open('performance_data.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Timestamp', 'PID', 'User', 'Priority', 'Nice', 'VSize', 'RSS', 'CPU Usage', 'Memory Usage', 'Time', 'Command'])
                writer.writerows(rows)
            
            messagebox.showinfo("Success", f"Performance data for {app_package} has been saved to performance_data.csv")
        
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PerformanceDataCollectorApp(root)
    root.mainloop()