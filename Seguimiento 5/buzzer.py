from machine import Pin, PWM
import time

buzzer_pin = PWM(Pin(27), freq=1000, duty=0)
ultimo_tono = 0

def buzzer_off():
    """Apaga el buzzer completamente"""
    buzzer_pin.duty(0)

def buzzer_on():
    """Tono genérico simple"""
    global ultimo_tono
    ahora = time.ticks_ms()
    if time.ticks_diff(ahora, ultimo_tono) > 500:
        buzzer_pin.init(freq=1000, duty=512)
        time.sleep(0.2)
        buzzer_pin.duty(0)
        ultimo_tono = ahora

# ============================================
# SONIDOS ESPECÍFICOS POR TIPO DE ALERTA
# ============================================

def buzzer_temp_baja():
    """❄️ Temperatura baja - 3 pulsos graves lentos"""
    global ultimo_tono
    ahora = time.ticks_ms()
    
    if time.ticks_diff(ahora, ultimo_tono) > 2000:
        for _ in range(3):
            buzzer_pin.init(freq=300, duty=512)
            time.sleep(0.25)
            buzzer_pin.duty(0)
            time.sleep(0.25)
        ultimo_tono = ahora

def buzzer_temp_alta():
    """🔥 Temperatura alta - Pitido agudo sostenido"""
    global ultimo_tono
    ahora = time.ticks_ms()
    
    if time.ticks_diff(ahora, ultimo_tono) > 1500:
        buzzer_pin.init(freq=2200, duty=700)
        time.sleep(0.6)
        buzzer_pin.duty(0)
        ultimo_tono = ahora

def buzzer_hum_baja():
    """🏜️ Humedad baja - 2 pitidos cortos medios"""
    global ultimo_tono
    ahora = time.ticks_ms()
    
    if time.ticks_diff(ahora, ultimo_tono) > 2000:
        for _ in range(2):
            buzzer_pin.init(freq=900, duty=512)
            time.sleep(0.12)
            buzzer_pin.duty(0)
            time.sleep(0.18)
        ultimo_tono = ahora

def buzzer_hum_alta():
    """💧 Humedad alta - Ondulante suave"""
    global ultimo_tono
    ahora = time.ticks_ms()
    
    if time.ticks_diff(ahora, ultimo_tono) > 1500:
        for freq in [800, 1200, 1600, 1200, 800]:
            buzzer_pin.init(freq=freq, duty=512)
            time.sleep(0.1)
        buzzer_pin.duty(0)
        ultimo_tono = ahora

def buzzer_ambas():
    """⚠️ Ambas fuera de rango - Sirena alternante"""
    global ultimo_tono
    ahora = time.ticks_ms()
    
    if time.ticks_diff(ahora, ultimo_tono) > 1000:
        for _ in range(4):
            buzzer_pin.init(freq=1800, duty=700)
            time.sleep(0.1)
            buzzer_pin.init(freq=600, duty=700)
            time.sleep(0.1)
        buzzer_pin.duty(0)
        ultimo_tono = ahora

def buzzer_panico():
    """🚨 Botón de pánico - Sirena aguda rápida"""
    global ultimo_tono
    ahora = time.ticks_ms()
    
    if time.ticks_diff(ahora, ultimo_tono) > 700:
        for _ in range(5):
            buzzer_pin.init(freq=2800, duty=1023)
            time.sleep(0.06)
            buzzer_pin.init(freq=400, duty=1023)
            time.sleep(0.06)
        buzzer_pin.duty(0)
        ultimo_tono = ahora
