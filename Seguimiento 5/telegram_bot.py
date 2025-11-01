import urequests
import time

TOKEN = '7935777862:AAFYFwGPMmI9Cy1AArMWEeMYVvJK4dBCYpM'
CHAT_ID = '8213202666'

# Umbrales (pueden cambiarse desde Telegram)
umbrales = {
    'temp_min': 18,
    'temp_max': 30,
    'hum_min': 30,
    'hum_max': 70
}

ultima_alerta_temp = 0
ultima_alerta_hum = 0
ultimo_update_id = 0

def enviar(texto):
    """Envía mensaje - MÉTODO QUE FUNCIONA"""
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        texto_limpio = texto.replace('"', "'").replace('\n', ' ')
        data_str = '{"chat_id":"' + CHAT_ID + '","text":"' + texto_limpio + '"}'
        response = urequests.post(url, data=data_str, headers={"Content-Type": "application/json"})
        response.close()
        return True
    except:
        return False

def enviar_ip(ip):
    """Envía IP al arrancar"""
    return enviar(f"ESP32 Conectado - IP: http://{ip}")

def alerta_panico():
    """Alerta de botón pánico"""
    return enviar("BOTON DE PANICO ACTIVADO - Requiere atencion inmediata")

def verificar_alertas(temp, hum):
    """Verifica y envía alertas (cada 5 min) - ALARMA SI ESTÁ FUERA DEL RANGO"""
    global ultima_alerta_temp, ultima_alerta_hum
    ahora = time.time()
    
    # ALERTA si temp < 18 o temp >= 30
    if temp < umbrales['temp_min'] or temp >= umbrales['temp_max']:
        if ahora - ultima_alerta_temp > 300:  # Cada 5 minutos
            if temp < umbrales['temp_min']:
                enviar(f"ALERTA: Temperatura BAJA {temp:.1f}C (rango normal: {umbrales['temp_min']}-{umbrales['temp_max']}C)")
            else:
                enviar(f"ALERTA: Temperatura ALTA {temp:.1f}C (rango normal: {umbrales['temp_min']}-{umbrales['temp_max']}C)")
            ultima_alerta_temp = ahora
    
    # ALERTA si hum < 30 o hum >= 70
    if hum < umbrales['hum_min'] or hum >= umbrales['hum_max']:
        if ahora - ultima_alerta_hum > 300:  # Cada 5 minutos
            if hum < umbrales['hum_min']:
                enviar(f"ALERTA: Humedad BAJA {hum:.1f}% (rango normal: {umbrales['hum_min']}-{umbrales['hum_max']}%)")
            else:
                enviar(f"ALERTA: Humedad ALTA {hum:.1f}% (rango normal: {umbrales['hum_min']}-{umbrales['hum_max']}%)")
            ultima_alerta_hum = ahora

def obtener_comandos():
    """Lee comandos de Telegram"""
    global ultimo_update_id
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={ultimo_update_id + 1}&timeout=1"
        response = urequests.get(url)
        data = response.json()
        response.close()
        
        if data.get('ok') and data.get('result'):
            for update in data['result']:
                ultimo_update_id = update['update_id']
                if 'message' in update and 'text' in update['message']:
                    procesar_comando(update['message']['text'])
        return True
    except:
        return False

def procesar_comando(cmd):
    """Procesa comandos"""
    from sensor import leer_sensor
    
    cmd = cmd.lower().strip()
    
    if cmd == '/start':
        enviar("Bot ESP32 Activo - Comandos disponibles: /datos (ver temp y hum) /umbrales (ver rangos) /temp_min 20 /temp_max 30 /hum_min 30 /hum_max 70")
    
    elif cmd == '/datos':
        temp, hum = leer_sensor()
        enviar(f"Temperatura: {temp:.1f}C - Humedad: {hum:.1f}%")
    
    elif cmd == '/umbrales':
        enviar(f"Rangos normales: Temp {umbrales['temp_min']}-{umbrales['temp_max']}C | Hum {umbrales['hum_min']}-{umbrales['hum_max']}%")
    
    elif cmd.startswith('/temp_min '):
        try:
            umbrales['temp_min'] = int(cmd.split()[1])
            enviar(f"OK - Temperatura minima actualizada: {umbrales['temp_min']}C")
        except:
            enviar("Error - Usa: /temp_min 20")
    
    elif cmd.startswith('/temp_max '):
        try:
            umbrales['temp_max'] = int(cmd.split()[1])
            enviar(f"OK - Temperatura maxima actualizada: {umbrales['temp_max']}C")
        except:
            enviar("Error - Usa: /temp_max 30")
    
    elif cmd.startswith('/hum_min '):
        try:
            umbrales['hum_min'] = int(cmd.split()[1])
            enviar(f"OK - Humedad minima actualizada: {umbrales['hum_min']}%")
        except:
            enviar("Error - Usa: /hum_min 30")
    
    elif cmd.startswith('/hum_max '):
        try:
            umbrales['hum_max'] = int(cmd.split()[1])
            enviar(f"OK - Humedad maxima actualizada: {umbrales['hum_max']}%")
        except:
            enviar("Error - Usa: /hum_max 70")
    
    else:
        enviar("Comando no reconocido. Usa /start para ver comandos")

def get_umbrales():
    """Retorna umbrales actuales"""
    return umbrales