# main.py

print("\n" + "="*40)
print("    ESP32 - SISTEMA DE MONITOREO")
print("="*40 + "\n")

try:
    # Importar y ejecutar el servidor web con Telegram
    print("📡 Iniciando servidor web y bot de Telegram...")
    
    import web_sensor
    
except KeyboardInterrupt:
    print("\n❌ Sistema detenido por usuario")
    
except Exception as e:
    print(f"\n❌ Error crítico: {e}")
    print("Reiniciando en 10 segundos...")
    import time
    time.sleep(10)
    import machine
    machine.reset()