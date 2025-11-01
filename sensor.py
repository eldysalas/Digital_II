import time

try:
    import dht
    from machine import Pin
    sensor = dht.DHT22(Pin(4))  # Cambia a DHT11 si es necesario
    SENSOR_OK = True
except:
    SENSOR_OK = False

temp_sim = 25
hum_sim = 60

def leer_sensor():
    global temp_sim, hum_sim

    if SENSOR_OK:
        try:
            sensor.measure()
            return sensor.temperature(), sensor.humidity()
        except:
            pass

    temp_sim += 1
    hum_sim += 1
    if temp_sim > 30: temp_sim = 25
    if hum_sim > 70: hum_sim = 60

    return temp_sim, hum_sim