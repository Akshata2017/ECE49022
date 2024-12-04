import machine
import time
import ujson
import network
import urequests
from machine import Pin, ADC
from machine import I2C, Pin
import random

# Wi-Fi credentials
ssid = "Manjunatha's iPhone"
password = "2k1129230"

# Firestore REST API URL
project_id = "iostest-4ba71"
collection_name = "devices"
firestore_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/{collection_name}/WcWydmQhgrcdwf0aKyIQ"

# OAuth Access Token
access_token = "ya29.a0AeDClZCTb_pd8LNKvvAQHGKxNbci9ofxK--ds0F8gJ4MCr1ApXjE3-oyVwVPizg69lISfjL-TL7oacwkCKKDxQJh_k8Nm2Hnx3eH1xUbTDfNCsjiq6A1-kqe3-bJr1E4PHAhu2uQijwuPH9aMzr3jmjzRF9NVbiLcTQd4ArwRQaCgYKAUMSARISFQHGX2Mic2zs0s9oPqTPDmI7w6eU_A0177"
# Function to connect to Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to Wi-Fi...")
        wlan.connect(ssid, password)
        for i in range(10):  # Try for 10 seconds
            if wlan.isconnected():
                break
            time.sleep(1)
            print(f"Attempt {i+1}: Still connecting...")
    if wlan.isconnected():
        print("Connected to Wi-Fi:", wlan.ifconfig())
    else:
        print("Failed to connect to Wi-Fi")
        raise OSError("Wi-Fi Connection Failed")

# Function to format time
def format_timestamp(hours_ahead=0):
    """Generate a timestamp with a specified offset in hours."""
    utc_time = time.gmtime(time.time() + hours_ahead * 3600)
    return "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}Z".format(
        utc_time[0], utc_time[1], utc_time[2], utc_time[3], utc_time[4], utc_time[5]
    )

# Function to simulate and append 3 hours' worth of data
def simulate_and_append():
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        # Fetch existing data from Firestore
        response = urequests.get(firestore_url, headers=headers)
        if response.status_code == 200:
            document_data = response.json()

            # Get the existing voltage, current, and power arrays
            current_voltages = document_data.get("fields", {}).get("voltage", {}).get("arrayValue", {}).get("values", [])
            current_currents = document_data.get("fields", {}).get("current", {}).get("arrayValue", {}).get("values", [])
            current_powers = document_data.get("fields", {}).get("power", {}).get("arrayValue", {}).get("values", [])
            timestamps = document_data.get("fields", {}).get("timestamp", {}).get("arrayValue", {}).get("values", [])

            # Normalize existing arrays
            normalized_voltages = [float(v["doubleValue"]) for v in current_voltages]
            normalized_currents = [float(c["doubleValue"]) for c in current_currents]
            normalized_powers = [float(p["doubleValue"]) for p in current_powers]
            normalized_timestamps = [t["stringValue"] for t in timestamps]

            # Simulate 3 hours' worth of data (6 points per hour)
            for hour in range(3):  # Simulate for 3 hours
                base_voltage = 5 + hour * 2  # Increment voltage for each hour
                base_current = 0.8 + hour * 0.3  # Increment current for each hour
                for point in range(6):  # 6 points per hour
                    voltage = round(base_voltage + random.uniform(-1, 1), 2)  # Add random noise
                    current = round(base_current + random.uniform(-0.2, 0.2), 2)  # Add random noise
                    power = round(voltage * current, 2)  # Calculate power
                    timestamp = format_timestamp(hours_ahead=hour)  # Adjust hour

                    # Append simulated data
                    normalized_voltages.append(voltage)
                    normalized_currents.append(current)
                    normalized_powers.append(power)
                    normalized_timestamps.append(timestamp)

            # Prepare payload
            payload = {
                "fields": {
                    "voltage1": {"arrayValue": {"values": [{"doubleValue": v} for v in normalized_voltages]}},
                    "current1": {"arrayValue": {"values": [{"doubleValue": c} for c in normalized_currents]}},
                    "power": {"arrayValue": {"values": [{"doubleValue": p} for p in normalized_powers]}},
                    "device_name": {"stringValue": "Simulated Device"},
                    "timestamp": {"arrayValue": {"values": [{"stringValue": t} for t in normalized_timestamps]}},
                }
            }

            # Send updated data to Firestore
            patch_response = urequests.patch(firestore_url, headers=headers, data=ujson.dumps(payload))
            if patch_response.status_code == 200:
                print("Simulated data successfully written to Firestore.")
            else:
                print(f"Failed to update Firestore: {patch_response.status_code}, {patch_response.text}")
            patch_response.close()
        else:
            print(f"Failed to fetch existing document: {response.status_code}, {response.text}")
        response.close()
    except Exception as e:
        print(f"Error during simulation and append: {e}")

# Main function
def main():
    connect_wifi()
    simulate_and_append()

main()
