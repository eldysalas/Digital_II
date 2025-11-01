import socket
from sensor import leer_sensor
from button import leer_boton
from buzzer import buzzer_off, buzzer_temp_baja, buzzer_temp_alta, buzzer_hum_baja, buzzer_hum_alta, buzzer_ambas, buzzer_panico
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
            .estado {
                padding: 15px;
                margin: 15px auto;
                max-width: 500px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 18px;
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
            
            /* ANIMACIONES DE PARPADEO DIFERENTES */
            @keyframes parpadeo_panico {
                0%, 100% { background-color: #ff0000; }
                50% { background-color: #330000; }
            }
            @keyframes parpadeo_temp_alta {
                0%, 100% { background-color: #ff4500; }
                50% { background-color: #ffccaa; }
            }
            @keyframes parpadeo_temp_baja {
                0%, 100% { background-color: #0066cc; }
                50% { background-color: #ccddff; }
            }
            @keyframes parpadeo_hum_alta {
                0%, 100% { background-color: #00aa00; }
                50% { background-color: #ccffcc; }
            }
            @keyframes parpadeo_hum_baja {
                0%, 100% { background-color: #ffaa00; }
                50% { background-color: #ffffcc; }
            }
            @keyframes parpadeo_ambas {
                0% { background-color: #ff0000; }
                25% { background-color: #ffaa00; }
                50% { background-color: #ff00ff; }
                75% { background-color: #ffaa00; }
                100% { background-color: #ff0000; }
            }
            
            .alerta_panico { animation: parpadeo_panico 0.5s infinite; }
            .alerta_temp_alta { animation: parpadeo_temp_alta 1s infinite; }
            .alerta_temp_baja { animation: parpadeo_temp_baja 1.5s infinite; }
            .alerta_hum_alta { animation: parpadeo_hum_alta 1.2s infinite; }
            .alerta_hum_baja { animation: parpadeo_hum_baja 1.3s infinite; }
            .alerta_ambas { animation: parpadeo_ambas 0.8s infinite; }
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
                    
                    // Remover todas las clases de animación
                    document.body.className = '';
                    
                    // Aplicar estilo según tipo de alerta
                    if (data.tipo_alerta == 'panico') {
                        document.body.className = 'alerta_panico';
                        document.getElementById('panic').innerText = "🔴 ACTIVADO";
                        document.getElementById('estado').innerHTML = "🚨 <strong>BOTÓN DE PÁNICO PRESIONADO</strong>";
                        document.getElementById('estado').style.background = "#ff0000";
                        document.getElementById('estado').style.color = "white";
                    }
                    else if (data.tipo_alerta == 'temp_baja') {
                        document.body.className = 'alerta_temp_baja';
                        document.getElementById('panic').innerText = "No";
                        document.getElementById('estado').innerHTML = "❄️ <strong>TEMPERATURA BAJA</strong><br>Temperatura: " + data.temperatura + "°C (mínimo: " + data.temp_min + "°C)";
                        document.getElementById('estado').style.background = "#0066cc";
                        document.getElementById('estado').style.color = "white";
                    }
                    else if (data.tipo_alerta == 'temp_alta') {
                        document.body.className = 'alerta_temp_alta';
                        document.getElementById('panic').innerText = "No";
                        document.getElementById('estado').innerHTML = "🔥 <strong>TEMPERATURA ALTA</strong><br>Temperatura: " + data.temperatura + "°C (máximo: " + data.temp_max + "°C)";
                        document.getElementById('estado').style.background = "#ff4500";
                        document.getElementById('estado').style.color = "white";
                    }
                    else if (data.tipo_alerta == 'hum_baja') {
                        document.body.className = 'alerta_hum_baja';
                        document.getElementById('panic').innerText = "No";
                        document.getElementById('estado').innerHTML = "🏜️ <strong>HUMEDAD BAJA</strong><br>Humedad: " + data.humedad + "% (mínimo: " + data.hum_min + "%)";
                        document.getElementById('estado').style.background = "#ffaa00";
                        document.getElementById('estado').style.color = "white";
                    }
                    else if (data.tipo_alerta == 'hum_alta') {
                        document.body.className = 'alerta_hum_alta';
                        document.getElementById('panic').innerText = "No";
                        document.getElementById('estado').innerHTML = "💧 <strong>HUMEDAD ALTA</strong><br>Humedad: " + data.humedad + "% (máximo: " + data.hum_max + "%)";
                        document.getElementById('estado').style.background = "#00aa00";
                        document.getElementById('estado').style.color = "white";
                    }
                    else if (data.tipo_alerta == 'ambas') {
                        document.body.className = 'alerta_ambas';
                        document.getElementById('panic').innerText = "No";
                        document.getElementById('estado').innerHTML = "⚠️ <strong>MÚLTIPLES ALERTAS</strong><br>Temperatura y humedad fuera de rango";
                        document.getElementById('estado').style.background = "#ff00ff";
                        document.getElementById('estado').style.color = "white";
                    }
                    else {
                        document.body.style.backgroundColor = "#f0f8ff";
                        document.getElementById('panic').innerText = "No";
                        document.getElementById('estado').innerHTML = "✅ <strong>Todo Normal</strong>";
                        document.getElementById('estado').style.background = "#00cc00";
                        document.getElementById('estado').style.color = "white";
                    }
                });
            }
            
            function apagar() {
                fetch('/apagar').then(() => actualizar());
            }
            
            setInterval(actualizar, 1000);
            window.onload = actualizar;
        </script>
    </head>
    <body>
        <h2>🌡 Monitor ESP32</h2>
        
        <div class="estado" id="estado">
            ✅ <strong>Cargando...</strong>
        </div>
        
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
        
        <p><small>🔄 Actualización automática cada segundo</small></p>
        <p><small>📱 Cambia umbrales desde Telegram con /temp_min, /temp_max, /hum_min, /hum_max</small></p>
    </body>
    </html>
    """

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('0.0.0.0', 80))
s.listen(5)
s.settimeout(0.1)
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
            
            # Verificar condiciones
            temp_baja = temp < umb['temp_min']
            temp_alta = temp >= umb['temp_max']
            hum_baja = hum < umb['hum_min']
            hum_alta = hum >= umb['hum_max']
            
            # Determinar tipo de alerta y activar buzzer correspondiente
            if boton:
                tipo_alerta = 'panico'
                buzzer_panico()
            elif (temp_baja or temp_alta) and (hum_baja or hum_alta):
                tipo_alerta = 'ambas'
                buzzer_ambas()
            elif temp_baja:
                tipo_alerta = 'temp_baja'
                buzzer_temp_baja()
            elif temp_alta:
                tipo_alerta = 'temp_alta'
                buzzer_temp_alta()
            elif hum_baja:
                tipo_alerta = 'hum_baja'
                buzzer_hum_baja()
            elif hum_alta:
                tipo_alerta = 'hum_alta'
                buzzer_hum_alta()
            else:
                tipo_alerta = 'normal'
                buzzer_off()
            
            # Botón pánico - enviar alerta por Telegram
            if TELEGRAM_OK and boton and not boton_anterior:
                telegram_bot.alerta_panico()
            boton_anterior = boton
            
            # Verificar alertas cada 10 seg
            if TELEGRAM_OK:
                ahora = time.time()
                if ahora - ultima_verificacion > 10:
                    telegram_bot.verificar_alertas(temp, hum)
                    ultima_verificacion = ahora
            
            json_data = '{{"temperatura": {:.1f}, "humedad": {:.1f}, "boton": {}, "temp_min": {}, "temp_max": {}, "hum_min": {}, "hum_max": {}, "tipo_alerta": "{}"}}'.format(
                temp, hum, int(boton), 
                umb['temp_min'], umb['temp_max'], umb['hum_min'], umb['hum_max'],
                tipo_alerta
            )
            conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n")
            conn.sendall(json_data.encode())
        
        elif "GET /apagar" in request:
            buzzer_off()
            conn.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
        
        conn.close()
        
    except OSError:
        pass
    
    # Procesar comandos de Telegram si está disponible
    if TELEGRAM_OK:
        telegram_bot.obtener_comandos()
