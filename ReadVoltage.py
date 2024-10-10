#from machine import ADC, Pin --> do I need to include this on mine? Or Akshata on hers?

def ReadVoltage():
    adc_pin = ADC(Pin(39))
    adc_value = adc_pin.read()  # Read the raw ADC value (0-6000)
    voltage = (adc_value - 3000) / 6000 * 100  # Convert to voltage 
    return voltage