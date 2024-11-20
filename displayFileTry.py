from machine import Pin
import time


def DisplayFile(voltage, current, power):
    voltage = 5.5
    current = 6.1
    power = 7.8

    d4 = Pin(25, Pin.OUT)
    d5 = Pin(26, Pin.OUT)
    d6 = Pin(27, Pin.OUT)
    d7 = Pin(18, Pin.OUT)

    rs = 0  # RS is tied to GND 
    en = 1  # EN is tied to 5.1V

    # Helper function to send a 4-bit nibble to the LCD
    def send_nibble(nibble):
        d4.value((nibble >> 0) & 1)
        d5.value((nibble >> 1) & 1)
        d6.value((nibble >> 2) & 1)
        d7.value((nibble >> 3) & 1)
        time.sleep_us(1)

    # Function to send a command to the LCD
    def send_command(command):
        send_nibble(command >> 4) 
        time.sleep_us(1)
        send_nibble(command & 0x0F) 
        time.sleep_ms(2) 

    def send_data(data):
        send_nibble(data >> 4) 
        send_nibble(data & 0x0F)
        time.sleep_ms(2)

    send_command(0x33)  # Initialize LCD in 4-bit mode (command repeated)
    send_command(0x32)  # Set to 4-bit mode
    send_command(0x28)  # 4-bit mode, 2 lines, 5x7 format
    send_command(0x0C)  # Display ON, cursor OFF
    send_command(0x06)  # Increment cursor, no shift
    send_command(0x01)  # Clear display

    for char in f"V:{voltage:.2f}":
        send_data(ord(char)) 

    send_command(0xC0) 
    for char in f"I:{current:.2f}":
        send_data(ord(char)) 

    send_command(0x94) 
    for char in f"P:{power:.2f}":
        send_data(ord(char)) 

    while True:
        time.sleep(1)
