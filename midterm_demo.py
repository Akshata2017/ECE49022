import machine
import time
import ujson
import network
import urequests
from machine import Pin, ADC
from machine import I2C, Pin
from lcd_api import LcdApi
from i2c_lcd import I2cLcd

# Wi-Fi credentials
ssid = "Manjunatha's iPhone"
password = '2k1129230'

# Firestore REST API URL
project_id = "iostest-4ba71" 
collection_name = "devices"  
firestore_url = f"https://firestore.googleapis.com/v1/projects/iostest-4ba71/databases/(default)/documents/devices/WcWydmQhgrcdwf0aKyIQ"

# OAuth Access Token
access_token = "ya29.c.c0ASRK0GbK8tYJjSwjmBnslQ-yj1FboqDeBeqHz0YSimhEo7gtnkeysS0n-kj7aRzCFSLJR-_f40CuMbaXjum6Nho1OQr0LF3N-RmxtJntAFqSJaDpnp-e6JSdZzNbt2DTbjmuepteuo7zQtz43Wr5IViTiYkOn46qGmHVCjs8y_Ogt5-Js7k1SN90JDGrwoTJIpvUV_E9XBWejcdw232IFLLwYu3iNLvW86epj7ce4vqskQIFPKVi5PN9MM5VdYJipSn19mFIrQewzZU8oWR4f85LqCUlNo223iZ-1mtSGNTivJXMjLXMKWOsOpJFHeD32GtGFdKNzWUEnrJ_X_TandBHfwjCKKyvgIKDkdtGEqcH1CDdfnFF09NYDWrDlaNK91oIyQL399ClJX7mB4s986opo3u6cojfnuWM1w3p6ptp-9tuyqR2-RXifujjtrlygrRO54YU1FOR2WtMhc_QOO7vS6BMtORvp62Sfg574XIW5Ym9X6klo-l3FabuXnetcaRFZ4udUucbX7iru8u7nvfnVgX3u_2RbsVVkdQrUVjyixam9U-R35topWStpyoY0UnZahMa9f1_almYuo4htfk0mzXe22IcfWbz5knxu2Q4gziX2cFJZudmdhfjgV8QMuY0aco3j0awWZXsyMdR6QI8hjmI6m0FwBMwkebqRs9m-46izUM8jnz5oYm5f9BilnnnmW-O1RF5Ju1JS9SRwBwyBFigfyWoQOVk7UfU2t40-4_yhrO96gefigZ49VFFZdUmXSBcn6l9M200btwX8xtzF_bMfm6jncVbQUX666dt2yZ2F2dlYkWFSuQakudqyQZtQqSSl3Umppfm5dMRR4vUsa2a8qrkf2cx5oUe59vpwJkj23rtJqvevRZjfa1I9aSpnJiJxzRfmIaugZQf27FUMe5VoosBaV87rY9Bh97jr5UbobUF_XFnJWw35mBjf_iMXqOyOOZM1IZblumqzMlsQlXZrZIuaOU3knRBze9hhpQXkcMVnWe"
# Throughput and Latency measurement variables
data_points = 0
start_time = time.time()

# Function to connect to Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to Wi-Fi...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            time.sleep(1)
    print('Connected to Wi-Fi:', wlan.ifconfig())

# Function to format time in EST
def format_timestamp():
    utc_time = time.gmtime(time.time())  # Get UTC time
    adjusted_hour = (utc_time[3] - 4) % 24  # Adjust for Eastern Time
    return "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}Z".format(utc_time[0], utc_time[1], utc_time[2], adjusted_hour, utc_time[4], utc_time[5])

# Function to append new voltage, current, and power to the existing arrays
def append_voltage_current_power(voltage, current, power):
    global data_points, start_time
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # Record the time before sending the request (for latency measurement)
        send_start_time = time.time()

        response = urequests.get(firestore_url, headers=headers)
        if response.status_code == 200:
            document_data = response.json()

            # Get the existing voltage, current, and power arrays
            current_voltages = document_data.get('fields', {}).get('voltage', {}).get('arrayValue', {}).get('values', [])
            current_currents = document_data.get('fields', {}).get('current', {}).get('arrayValue', {}).get('values', [])
            current_powers = document_data.get('fields', {}).get('power', {}).get('arrayValue', {}).get('values', [])

            # Normalize arrays and append new values
            normalized_voltages = [float(v['doubleValue']) if 'doubleValue' in v else float(v['integerValue']) for v in current_voltages]
            normalized_currents = [float(c['doubleValue']) if 'doubleValue' in c else float(c['integerValue']) for c in current_currents]
            normalized_powers = [float(p['doubleValue']) if 'doubleValue' in p else float(p['integerValue']) for p in current_powers]

            # Append new values
            normalized_voltages.append(voltage)
            normalized_currents.append(current)
            normalized_powers.append(power)
        

            # Prepare payload (JSON) with updated arrays
            payload = {
                "fields": {
                    "voltage": {"arrayValue": {"values": [{"doubleValue": v} for v in normalized_voltages]}},
                    "current": {"arrayValue": {"values": [{"doubleValue": c} for c in normalized_currents]}},
                    "power": {"arrayValue": {"values": [{"doubleValue": p} for p in normalized_powers]}},
                    "timestamp": {"timestampValue": format_timestamp()},
                    "device_name": {"stringValue": "Midterm Demo Device"}
                }
            }
            # print the payload being sent
           # print(f"Sending payload to Firestore: {ujson.dumps(payload)}")


            # Send the updated arrays to Firestore
            patch_response = urequests.patch(firestore_url, headers=headers, data=ujson.dumps(payload))

            # Record the time after receiving the response (for latency measurement)
            receive_end_time = time.time()

            # Calculate and display latency
            latency = receive_end_time - send_start_time
            print(f"Data updated: {patch_response.status_code}")
            print(f"Latency: {latency:.4f} seconds")  # Display latency

            # Increment data point counter
            data_points += 1

            # Calculate throughput every minute
            elapsed_time = time.time() - start_time
            if elapsed_time >= 60:
                throughput = data_points / (elapsed_time / 60)
                print(f"Throughput: {throughput:.2f} data points per minute")
                # Reset for the next minute
                data_points = 0
                start_time = time.time()

            patch_response.close()
        else:
            print(f"Failed to fetch document: {response.status_code}")
            print(response.text)
        
        response.close()
    except Exception as e:
        print(f"Failed to append voltage, current, and power: {e}")

# Function to display data on the LCD
def DisplayFile(voltage, current, power):
    # ESP32 I2C configuration
    i2c = I2C(0, scl=Pin(4), sda=Pin(14), freq=400000)

    # LCD address and screen dimensions
    I2C_ADDR = 0x27  # Common I2C address for 20x4 LCD
    LCD_ROWS = 4
    LCD_COLS = 20

    # Initialize the LCD display
    lcd = I2cLcd(i2c, I2C_ADDR, LCD_ROWS, LCD_COLS)

    # Clear the screen and display text
    lcd.clear()
    lcd.move_to(0, 0)  # First line, first column
    lcd.putstr(f"Voltage: {voltage:.2f} V")
    lcd.move_to(0, 1)  # Second line, first column
    lcd.putstr(f"Current: {current:.2f} A")
    lcd.move_to(0, 2)  # Third line, first column
    lcd.putstr(f"Power: {power:.2f} W")

# Function to read voltage from ADC pin
def ReadVoltage():
    adc_pin = ADC(Pin(32))  
    adc_value = adc_pin.read() 
    voltage = (adc_value - 3000) / 6000 * 100
    return voltage

# Dummy current value generator
def read_current():
    current = 4 
    return current

# Main function
def main():
    connect_wifi()

    while True:
        voltage = ReadVoltage()  # Read sensor voltage
        current = read_current()  # Read dummy current
        power = voltage * current  # Calculate power
        DisplayFile(voltage, current, power)
        append_voltage_current_power(voltage, current, power)  # Upload data
        time.sleep(6)  # Wait 6 seconds between uploads

main()
# need to update the timestamp data (wrong timezone rn)
# need to update the authentication (access token is not feasible long term)
# google data studio portion has to be added
