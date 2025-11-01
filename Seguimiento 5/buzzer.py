from machine import Pin

# Usaremos el GPIO 27 para el buzzer (puedes cambiarlo si necesitas)
buzzer = Pin(27, Pin.OUT)

def buzzer_on():
    buzzer.value(1)

def buzzer_off():
    buzzer.value(0)
