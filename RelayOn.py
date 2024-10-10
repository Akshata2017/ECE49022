#from machine import Pin

def RelayOn():
    relay = Pin(25, Pin.OUT)
    relay.value(1)
    return