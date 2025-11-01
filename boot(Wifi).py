# boot.py - Conexión WiFi simple
import network
import time

SSID = 'SHAIRA'         # <-- escribe aquí el nombre exacto de tu WiFi
PASSWORD = '18041989' # <-- escribe aquí la contraseña de tu WiFi

print("Iniciando conexión WiFi...")
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

for i in range(20):
    if wlan.isconnected():
        break
    print(".", end="")
    time.sleep(1)

if wlan.isconnected():
    print("\n✅ Conectado a WiFi:", wlan.ifconfig())
else:
    print("\n❌ No se pudo conectar. Revisa SSID o contraseña.")
