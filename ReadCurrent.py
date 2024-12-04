# Code to obtain current measurements
# ECE 49022 - Household Power Consumption Meter
# Megan Wagner : 12/3/2024

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
    
    current = ((voltage - v_zero) / (vcc / 2)) * current_range # Convert the voltage to current
    return current

