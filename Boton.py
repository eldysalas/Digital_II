from machine import Pin

# GPIO14 como botón (puedes cambiarlo si usas otro pin)
boton = Pin(14, Pin.IN, Pin.PULL_UP)

def leer_boton():
    return boton.value() == 0  # True si se presiona (va a GND)
