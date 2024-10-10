#from machine import I2C, Pin
#from lcd_api import LcdApi
#from i2c_lcd import I2cLcd
#import time

def DiplayFile(voltage, current, power):
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
    lcd.move_to(0,2)  # Third line, first column
    lcd.putstr(f"Power: {power:.2f} W")

    # Keep the display on
    while True:
        time.sleep(1)
        
    return
    
