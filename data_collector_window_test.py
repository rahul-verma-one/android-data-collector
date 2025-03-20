import tkinter as tk
from tkinter import messagebox, filedialog
import subprocess
from app import DataCollectorApp


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

        return sorted_process_names



if __name__ == "__main__":
    dataUI = DataCollectorUI()


"""
def on_button_click():
    entered_text = entry.get()
    messagebox.showinfo("Information", f"You entered: {entered_text}")

def open_file():
    file_path = filedialog.askopenfilename()
    messagebox.showinfo("Selected File", f"Selected file: {file_path}")

root = tk.Tk()
root.title("Tkinter Crash Course")
root.geometry("400x300")

label = tk.Label(root, text="Enter something:")
label.pack(pady=5)

entry = tk.Entry(root)
entry.pack(pady=5)

button = tk.Button(root, text="Show Entry", command=on_button_click)
button.pack(pady=5)

file_button = tk.Button(root, text="Open File", command=open_file)
file_button.pack(pady=5)

root.mainloop()
"""