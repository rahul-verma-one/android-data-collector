import subprocess
import re

def get_network_usage(package_name):
    try:
        # Get the UID
        uid_process = subprocess.run(['adb', 'shell', 'dumpsys', 'package', package_name], capture_output=True, text=True)
        uid_match = re.search(r'userId=(\d+)', uid_process.stdout)
        if not uid_match:
            return "UID not found"
        uid = uid_match.group(1)

        # Get network stats
        netstats_process = subprocess.run(['adb', 'shell', 'dumpsys', 'netstats'], capture_output=True, text=True)
        netstats_lines = netstats_process.stdout.splitlines()

        total_rx_bytes = 0
        total_tx_bytes = 0

        for line in netstats_lines:
            if f"UID={uid}" in line:
                match = re.search(r'rxBytes=(\d+)\s+rxPkts=\d+\s+txBytes=(\d+)\s+txPkts=\d+', line)
                if match:
                    total_rx_bytes += int(match.group(1))
                    total_tx_bytes += int(match.group(2))

        return f"Rx Bytes: {total_rx_bytes}, Tx Bytes: {total_tx_bytes}"

    except Exception as e:
        return f"Error: {e}"

package_name = "com.facebook.katana"  # Replace with your package name
network_usage = get_network_usage(package_name)
print(network_usage)