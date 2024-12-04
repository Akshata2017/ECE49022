# Code to obtain voltage measurements
# ECE 49022 - Household Power Consumption Meter
# Megan Wagner : 12/3/2024

def ReadVoltage():
    # Configuration
    adc_pin = 39  # GPIO pin connected to ZMPT101's OUT pin
    vcc = 3.3  # Operating voltage of the sensor
    adc_resolution = 4096  # 12-bit ADC on ESP32
    calibration_factor = 100.0  # Adjust this value for accurate voltage measurements

    # Initialize ADC
    adc = ADC(Pin(ADC_PIN))
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

    return actual_voltage

