from machine import I2C, Pin, Timer, ADC
from i2c_lcd import I2cLcd
import time
import machine
import time
import ujson
import network
import urequests
import socket

# for display pins
display_scl_pin_number = 4
display_sda_pin_number = 14

# for voltage pin
read_voltage_pin_number = 32

# for current pin
read_current_pin_number = 33

# for relay
relay_pin_number = 25

# Wi-Fi credentials
ssid = "Manjunatha's iPhone"
password = '2k1129230'

# Firestore REST API URL
project_id = "iostest-4ba71" 
collection_name = "devices"  
firestore_url = f"https://firestore.googleapis.com/v1/projects/iostest-4ba71/databases/(default)/documents/devices/WcWydmQhgrcdwf0aKyIQ"

# OAuth Access Token
access_token = "ya29.c.c0ASRK0GbK8tYJjSwjmBnslQ-yj1FboqDeBeqHz0YSimhEo7gtnkeysS0n-kj7aRzCFSLJR-_f40CuMbaXjum6Nho1OQr0LF3N-RmxtJntAFqSJaDpnp-e6JSdZzNbt2DTbjmuepteuo7zQtz43Wr5IViTiYkOn46qGmHVCjs8y_Ogt5-Js7k1SN90JDGrwoTJIpvUV_E9XBWejcdw232IFLLwYu3iNLvW86epj7ce4vqskQIFPKVi5PN9MM5VdYJipSn19mFIrQewzZU8oWR4f85LqCUlNo223iZ-1mtSGNTivJXMjLXMKWOsOpJFHeD32GtGFdKNzWUEnrJ_X_TandBHfwjCKKyvgIKDkdtGEqcH1CDdfnFF09NYDWrDlaNK91oIyQL399ClJX7mB4s986opo3u6cojfnuWM1w3p6ptp-9tuyqR2-RXifujjtrlygrRO54YU1FOR2WtMhc_QOO7vS6BMtORvp62Sfg574XIW5Ym9X6klo-l3FabuXnetcaRFZ4udUucbX7iru8u7nvfnVgX3u_2RbsVVkdQrUVjyixam9U-R35topWStpyoY0UnZahMa9f1_almYuo4htfk0mzXe22IcfWbz5knxu2Q4gziX2cFJZudmdhfjgV8QMuY0aco3j0awWZXsyMdR6QI8hjmI6m0FwBMwkebqRs9m-46izUM8jnz5oYm5f9BilnnnmW-O1RF5Ju1JS9SRwBwyBFigfyWoQOVk7UfU2t40-4_yhrO96gefigZ49VFFZdUmXSBcn6l9M200btwX8xtzF_bMfm6jncVbQUX666dt2yZ2F2dlYkWFSuQakudqyQZtQqSSl3Umppfm5dMRR4vUsa2a8qrkf2cx5oUe59vpwJkj23rtJqvevRZjfa1I9aSpnJiJxzRfmIaugZQf27FUMe5VoosBaV87rY9Bh97jr5UbobUF_XFnJWw35mBjf_iMXqOyOOZM1IZblumqzMlsQlXZrZIuaOU3knRBze9hhpQXkcMVnWe"


def connect_to_wifi() -> str:
    """returns the IP address"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    time.sleep(5)  # this gives the wifi a better chance of connecting

    for _ in range(10):
        try:
            wlan.connect(ssid, password)
            time.sleep(2)
            if wlan.isconnected():   
                break
        except OSError:
            time.sleep(1)
    else:
        raise Exception("Wifi was unable to connect")

    return wlan.ifconfig()[0]


def display_data(voltage, current, power):

    # ESP32 I2C configuration
    i2c = I2C(0, scl=Pin(display_scl_pin_number), sda=Pin(display_sda_pin_number), freq=400000)

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


def read_voltage() -> float:
    adc_pin = ADC(Pin(read_voltage_pin_number))  
    adc_value = adc_pin.read() 
    voltage = (adc_value - 4095) * 3.3
    return voltage


def read_current() -> float:
    current = 4 
    return current


def update_replay(relay_status: bool):
    relay = Pin(relay_pin_number, Pin.OUT)
    relay.value(relay_status)
    return


def append_voltage_current_power(voltage, current, power):
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # Record the time before sending the request (for latency measurement)

        response = urequests.get(firestore_url, headers=headers)

        if response.status_code != 200:
            raise Exception("Not a 200 Response") 
            
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
                "device_name": {"stringValue": "Midterm Demo Device"}
            }
        }

        # Send the updated arrays to Firestore
        patch_response = urequests.patch(firestore_url, headers=headers, data=ujson.dumps(payload))
        patch_response.close()
        
        response.close()

    except Exception as e:
        print(f"Failed to append voltage, current, and power: {e}")


def main_callback(timer):
    voltage = read_voltage()
    current = read_current()
    power = voltage * current
    display_data(voltage, current, power)
    append_voltage_current_power(voltage, current, power) 


def main():
    ip_address = connect_to_wifi()

    main_timer = Timer(0)
    sixty_seconds = 60_000
    main_timer.init(period=sixty_seconds, mode=Timer.PERIODIC, callback=main_callback)

    while True:
        addr = socket.getaddrinfo(ip_address, 80)[0][-1]
        s = socket.socket()
        s.bind(addr)
        s.listen(5) 

        cl, addr = s.accept()
        request = cl.recv(1024)

        update_replay("relay-on" in request)

        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            "Connection: close\r\n"
            "\r\n"
            "Relay status updated"
        )
        cl.send(response.encode('utf-8'))

        cl.close()


if __name__ == '__main__':
    main()
