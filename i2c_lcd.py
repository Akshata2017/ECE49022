import time
from lcd_api import LcdApi
from machine import Pin

DEFAULT_I2C_ADDR = 0x27  # The default I2C address for many LCDs

MASK_RS = 0x01
MASK_RW = 0x02
MASK_E = 0x04
SHIFT_BACKLIGHT = 3
SHIFT_DATA = 4

class I2cLcd(LcdApi):
    """Implements a HD44780 character LCD connected via PCF8574 on I2C."""

    def __init__(self, i2c, i2c_addr=DEFAULT_I2C_ADDR, num_lines=4, num_columns=20):
        # Accepts the I2C instance directly
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.backlight = True  # Default backlight state
        time.sleep(0.020)  # Allow LCD time to power up

        # Send reset 3 times
        self.hal_write_init_nibble(self.LCD_FUNCTION_RESET)
        time.sleep(0.005)  # Wait at least 4.1ms
        self.hal_write_init_nibble(self.LCD_FUNCTION_RESET)
        time.sleep(0.001)
        self.hal_write_init_nibble(self.LCD_FUNCTION_RESET)
        time.sleep(0.001)

        # Put LCD into 4-bit mode
        self.hal_write_init_nibble(self.LCD_FUNCTION)
        time.sleep(0.001)

        # Initialize the LCD using the parent class (LcdApi)
        LcdApi.__init__(self, num_lines, num_columns)

        cmd = self.LCD_FUNCTION
        if num_lines > 1:
            cmd |= self.LCD_FUNCTION_2LINES
        self.hal_write_command(cmd)

    def hal_write_init_nibble(self, nibble):
        """Writes an initialization nibble to the LCD."""
        byte = ((nibble >> 4) & 0x0f) << SHIFT_DATA
        self.i2c.writeto(self.i2c_addr, bytes([byte | MASK_E]))
        self.i2c.writeto(self.i2c_addr, bytes([byte]))

    def hal_backlight_on(self):
        """Turns the backlight on."""
        self.i2c.writeto(self.i2c_addr, bytes([1 << SHIFT_BACKLIGHT]))

    def hal_backlight_off(self):
        """Turns the backlight off."""
        self.i2c.writeto(self.i2c_addr, bytes([0]))

    def hal_sleep_us(self, usecs):
        """Sleep for the given microseconds."""
        time.sleep(usecs / 1000000)

    def hal_write_command(self, cmd):
        """Writes a command to the LCD."""
        byte = ((self.backlight << SHIFT_BACKLIGHT) |
                ((cmd >> 4) & 0x0f) << SHIFT_DATA)
        self.i2c.writeto(self.i2c_addr, bytes([byte | MASK_E]))
        self.i2c.writeto(self.i2c_addr, bytes([byte]))
        
        byte = ((self.backlight << SHIFT_BACKLIGHT) |
                ((cmd & 0x0f) << SHIFT_DATA))
        self.i2c.writeto(self.i2c_addr, bytes([byte | MASK_E]))
        self.i2c.writeto(self.i2c_addr, bytes([byte]))

        if cmd <= 3:
            time.sleep(0.005)  # Commands like home or clear take longer

    def hal_write_data(self, data):
        """Writes data to the LCD."""
        byte = (MASK_RS |
                (self.backlight << SHIFT_BACKLIGHT) |
                (((data >> 4) & 0x0f) << SHIFT_DATA))
        self.i2c.writeto(self.i2c_addr, bytes([byte | MASK_E]))
        self.i2c.writeto(self.i2c_addr, bytes([byte]))

        byte = (MASK_RS |
                (self.backlight << SHIFT_BACKLIGHT) |
                ((data & 0x0f) << SHIFT_DATA))
        self.i2c.writeto(self.i2c_addr, bytes([byte | MASK_E]))
        self.i2c.writeto(self.i2c_addr, bytes([byte]))
