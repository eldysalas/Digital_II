import socket
from sensor import leer_sensor
from button import leer_boton
from buzzer import buzzer_on, buzzer_off
import time

# TELEGRAM
try:
    import telegram_bot
    import network
    wlan = network.WLAN(network.STA_IF)
    telegram_bot.enviar_ip(wlan.ifconfig()[0])
    print("✅ Telegram activado")
    TELEGRAM_OK = True
except:
    print("⚠️ Telegram no disponible")
    TELEGRAM_OK = False

# Variables
boton_anterior = 0
ultima_verificacion = 0
TEMP_MIN = 18
TEMP_MAX = 30
HUM_MIN = 30
HUM_MAX = 70

def web_page():
    if TELEGRAM_OK:
        umb = telegram_bot.get_umbrales()
    else:
        umb = {'temp_min': TEMP_MIN, 'temp_max': TEMP_MAX, 'hum_min': HUM_MIN, 'hum_max': HUM_MAX}
    
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>ESP32 Sensor</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                background-color: #f0f8ff;
                padding: 20px;
            }
            h2 { color: #0078D7; }
            .datos {
                font-size: 24px;
                margin: 20px;
            }
            .umbral {
                background: #e0e0e0;
                padding: 15px;
                margin: 20px auto;
                border-radius: 8px;
                max-width: 400px;
            }
            button {
                background: #0078D7;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin: 10px;
            }
            button:hover { background: #005a9e; }
        </style>
        <script>
            function actualizar() {
                fetch('/data')
                .then(res => res.json())
                .then(data => {
                    document.getElementById('temp').innerText = data.temperatura + " °C";
                    document.getElementById('hum').innerText = data.humedad + " %";
                    document.getElementById('temp_min').innerText = data.temp_min;
                    document.getElementById('temp_max').innerText = data.temp_max;
                    document.getElementById('hum_min').innerText = data.hum_min;
                    document.getElementById('hum_max').innerText = data.hum_max;
                    
                    if (data.boton == 1) {
                        document.body.style.backgroundColor = "#ff4d4d";
                        document.getElementById('panic').innerText = "🔴 ACTIVADO";
                    }
                    else if (data.alerta == 1) {
                        document.body.style.backgroundColor = "#ffcccc";
                        document.getElementById('panic').innerText = "No";
                    }
                    else {
                        document.body.style.backgroundColor = "#f0f8ff";
                        document.getElementById('panic').innerText = "No";
                    }
                });
            }
            
            function apagar() {
                fetch('/apagar').then(() => actualizar());
            }
            
            setInterval(actualizar, 2000);
            window.onload = actualizar;
        </script>
    </head>
    <body>
        <h2>🌡 Monitor ESP32</h2>
        
        <div class="datos">
            <p><strong>Temperatura:</strong> <span id="temp">--</span></p>
            <p><strong>Humedad:</strong> <span id="hum">--</span></p>
            <p><strong>Botón de pánico:</strong> <span id="panic">No</span></p>
        </div>
        
        <div class="umbral">
            <h3>⚙️ Rangos Normales</h3>
            <p>🌡️ Temperatura: <span id="temp_min">--</span>°C a <span id="temp_max">--</span>°C</p>
            <p>💧 Humedad: <span id="hum_min">--</span>% a <span id="hum_max">--</span>%</p>
            <small>⚠️ Alarma si está FUERA de estos rangos</small>
        </div>
        
        <button onclick="apagar()">🔕 Apagar Alarma</button>
        
        <p><small>🔄 Actualización automática cada 2 segundos</small></p>
        <p><small>📱 Cambia umbrales desde Telegram con /temp_min, /temp_max, /hum_min, /hum_max</small></p>
    </body>
    </html>
    """

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('0.0.0.0', 80))
s.listen(5)
s.settimeout(0.5)
print("✅ Web activa en http://192.168.1.10")

while True:
    try:
        conn, addr = s.accept()
        request = conn.recv(1024).decode()
        
        if "GET / " in request:
            response = web_page()
            conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
            conn.sendall(response.encode())
        
        elif "GET /data" in request:
            temp, hum = leer_sensor()
            boton = leer_boton()
            
            if TELEGRAM_OK:
                umb = telegram_bot.get_umbrales()
            else:
                umb = {'temp_min': TEMP_MIN, 'temp_max': TEMP_MAX, 'hum_min': HUM_MIN, 'hum_max': HUM_MAX}
            
            # ALARMA si está FUERA del rango: temp<18 o temp>=30 o hum<30 o hum>=70
            alerta = 1 if (temp < umb['temp_min'] or temp >= umb['temp_max'] or 
                          hum < umb['hum_min'] or hum >= umb['hum_max'] or boton) else 0
            
            if alerta:
                buzzer_on()
            else:
                buzzer_off()
            
            # Botón pánico
            if TELEGRAM_OK and boton and not boton_anterior:
                telegram_bot.alerta_panico()
            boton_anterior = boton
            
            # Verificar alertas cada 10 seg
            if TELEGRAM_OK:
                ahora = time.time()
                if ahora - ultima_verificacion > 10:
                    telegram_bot.verificar_alertas(temp, hum)
                    ultima_verificacion = ahora
            
            json_data = '{{"temperatura": {:.1f}, "humedad": {:.1f}, "alerta": {}, "boton": {}, "temp_min": {}, "temp_max": {}, "hum_min": {}, "hum_max": {}}}'.format(
                temp, hum, alerta, int(boton), 
                umb['temp_min'], umb['temp_max'], umb['hum_min'], umb['hum_max']
            )
            conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n")
            conn.sendall(json_data.encode())
        
        elif "GET /apagar" in request:
            buzzer_off()
            conn.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
        
        conn.close()
        
    except OSError:
        if TELEGRAM_OK:
            telegram_bot.obtener_comandos()