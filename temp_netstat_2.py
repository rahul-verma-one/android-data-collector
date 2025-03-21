import subprocess
import re

def get_network_usage(package_name):
    try:
        # Get the UID of the package
        uid_process = subprocess.run(['adb', 'shell', 'dumpsys', 'package', package_name], capture_output=True, text=True)
        uid_match = re.search(r'userId=(\d+)', uid_process.stdout)
        if not uid_match:
            return "UID not found"
        uid = uid_match.group(1)

        # Get network usage from xt_qtaguid stats
        netstats_process = subprocess.run(['adb', 'shell', 'cat', '/proc/net/xt_qtaguid/stats'], capture_output=True, text=True)
        netstats_lines = netstats_process.stdout.splitlines()

        total_rx_bytes = 0
        total_tx_bytes = 0

        # The expected format: idx iface acct_tag_hex uid_tag_int cnt_set rx_bytes rx_packets tx_bytes tx_packets ...
        for line in netstats_lines:
            columns = line.split()
            if len(columns) > 4 and columns[3] == uid:
                total_rx_bytes += int(columns[5])  # rx_bytes
                total_tx_bytes += int(columns[7])  # tx_bytes

        return f"Rx Bytes: {total_rx_bytes}, Tx Bytes: {total_tx_bytes}"

    except Exception as e:
        return f"Error: {e}"

package_name = "com.facebook.katana"  # Replace with your package name
network_usage = get_network_usage(package_name)
print(network_usage)
