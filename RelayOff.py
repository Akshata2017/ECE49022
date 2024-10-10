#from machine import Pin

def RelayOff():
    relay = Pin(25, Pin.OUT)
    relay.value(0)
    return