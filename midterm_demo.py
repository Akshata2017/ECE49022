import machine
import time
import ujson
import network
import urequests
import math
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
firestore_url = f"https://firestore.googleapis.com/v1/projects/iostest-4ba71/databases/(default)/documents/devices/mirror_test"

# OAuth Access Token
data_points = 0
access_token = "ya29.a0AeDClZB0msokLvcBQsBmh9eGmbLVDFQ5D0hk6Y9Tq1_NOQuAp0fb8_0fGs9DNfzKFEvaioWGpa7pgTJvj5ADDMCA1X8e1SeyF3pE18RCBXcFUDYIDhwvAz6eQBUwLCfa4upYxpZaCNGMUsPGrvHO-KAA17COmz8j4T2kKnJbCwaCgYKAeQSARISFQHGX2MiMOJGjbR2MuaI7kuWDNtDGQ0177"

start_time = time.time()

# Function to connect to Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to Wi-Fi...')
        wlan.connect(ssid, password)
        for i in range(10):  # Try for 10 seconds
            if wlan.isconnected():
                break
            time.sleep(1)
            print(f"Attempt {i+1}: Still connecting...")
    if wlan.isconnected():
        print('Connected to Wi-Fi:', wlan.ifconfig())
    else:
        print('Failed to connect to Wi-Fi')
        raise OSError("Wi-Fi Connection Failed")


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
    #i2c = I2C(0, freq=400000)

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
    print(f"Refresh Rate: Once every 6 seconds.")
    
# Function to read voltage from ADC pin
def ReadVoltage():
    # Configuration
    adc_pin = 39  # GPIO pin connected to ZMPT101's OUT pin
    vcc = 5.1  # Operating voltage of the sensor
    adc_resolution = 4096  # 12-bit ADC on ESP32
    calibration_factor = 100.0  # Adjust this value for accurate voltage measurements

    # Initialize ADC
    adc = ADC(Pin(adc_pin))
    adc.atten(ADC.ATTN_11DB)  # Allow voltage range up to ~3.6V
    adc.width(ADC.WIDTH_12BIT)  # Set ADC resolution to 12-bit

    # Collect multiple samples to compute RMS
    samples = 100
    squared_sum = 0
    for _ in range(samples):
        raw_value = adc.read() # Convert the raw ADC value to voltage
        voltage = (raw_value / adc_resolution) * vcc # Subtract offset (centered at VCC/2 for AC signal)
        voltage -= vcc / 2 # Square the adjusted voltage
        squared_sum += voltage ** 2
        time.sleep(0.001)  # Small delay between samples

    # Calculate the RMS voltage
    mean_square = squared_sum / samples
    rms_voltage = math.sqrt(mean_square)

    # Convert to actual voltage using the calibration factor
    actual_voltage = rms_voltage * calibration_factor
    print(f"RMS: {rms_voltage:.4f}")
    print(f"RAW_VOLTAGE: {raw_value:.4f}")
    
    return actual_voltage
def ReadCurrent():
    # Configuration 
    adc_pin = 34
    vcc = 5.1 #operating voltage of sensor
    adc_resolution = 4096 #12-bit ADC on the ESP32
    current_range = 20.0 #full scale current range in Amps
    v_zero = vcc / 2 # sensor's zero-current voltage (assumes mid-scale at 0A)
    
    # Initialization 
    adc = ADC(Pin(adc_pin))
    adc.atten(ADC.ATTN_11DB)  # Set input attenuation to allow a larger voltage range (0-3.6V)
    adc.width(ADC.WIDTH_12BIT)  # Set ADC resolution to 12-bit
    
    # Collect measurement
    raw_value = adc.read()  # Read the raw analog value
    voltage = (raw_value / adc_resolution) * vcc # Convert the raw ADC value to a voltage
    
    current = ((voltage - 1.494) / (vcc / 2)) * current_range # Convert the voltage to current
    print(f"RAW_CURRENT: {raw_value:.4f}")
    return current



# Main function
def main():
    connect_wifi()

    while True:
        voltage = ReadVoltage()  # Read sensor voltage
        current = ReadCurrent()  # Read sensor current
        power = voltage * current  # Calculate power
        DisplayFile(voltage, current, power)
        append_voltage_current_power(voltage, current, power)  # Upload data
        time.sleep(6)  # Wait 6 seconds between uploads

main()


