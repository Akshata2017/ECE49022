import network
import urequests
import ubinascii
import time
import random 

# Wi-Fi credentials
ssid = "Manjunatha's iPhone" 
password = "2k1129230"      

# Twilio credentials
TWILIO_ACCOUNT_SID =  
TWILIO_AUTH_TOKEN =  
TWILIO_PHONE_NUMBER = '+16814594382' 
RECIPIENT_PHONE_NUMBER = '+5712309024'

# Power threshold
POWER_THRESHOLD = 200 

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to Wi-Fi...')
        wlan.connect(ssid, password)
        for i in range(15): 
            if wlan.isconnected():
                break
            time.sleep(1)
            print(f"Attempt {i+1}: Still connecting...")
    if wlan.isconnected():
        print("Connected to Wi-Fi:", wlan.ifconfig())
    else:
        print("Failed to connect to Wi-Fi")
        raise OSError("Wi-Fi Connection Failed")
    
def get_power_consumption():
    return random.uniform(200, 250)  # Simulated random power consumption

def send_sms(message):
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
    
    credentials = f"{TWILIO_ACCOUNT_SID}:{TWILIO_AUTH_TOKEN}"
    auth_header = ubinascii.b2a_base64(credentials.encode()).decode().strip()
    
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    payload = f"From={TWILIO_PHONE_NUMBER}&To={RECIPIENT_PHONE_NUMBER}&Body={message}"
    
    try:
        response = urequests.post(url, headers=headers, data=payload)
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.text}")
        
        if response.status_code == 201:
            print(f"Message sent successfully to {RECIPIENT_PHONE_NUMBER}.")
            print(f"Message content: {message}")
        elif response.status_code == 400:
            print("Failed to send message. Likely cause: The phone number is not verified with Twilio.")
        else:
            print(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")
        response.close()
    except Exception as e:
        print("An error occurred:", e)

def main():
    connect_wifi()
    print("Wi-Fi connected. Starting power monitoring...")

    while True:
        power = get_power_consumption()
        print(f"Current power consumption: {power:.2f}W")
        
        if power > POWER_THRESHOLD:
            send_sms(f"Power consumption has exceeded {POWER_THRESHOLD}W. Current power: {power:.2f}W.")
        
        time.sleep(60) 

main()
