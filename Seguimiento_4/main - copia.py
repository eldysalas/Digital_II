from machine import Pin, I2C, PWM
import framebuf, time
try: 
    import urandom #Para traer numeros random: Genera las coordenadas aleatorias de dónde aparece la comida
except:
    import random as urandom

#Driver parq eu el OLED duncione
class SSD1306:
    def __init__(self, width, height, i2c, addr=0x3C):
        self.width = width 
        self.height = height
        self.i2c = i2c
        self.addr = addr
        self.buffer = bytearray(self.height * self.width // 8)
        self.fb = framebuf.FrameBuffer(self.buffer, self.width, self.height, framebuf.MONO_VLSB)
        self.init_display()

    def write_cmd(self, cmd):
        self.i2c.writeto(self.addr, bytearray([0x80, cmd]))

    def init_display(self):
        for cmd in (
            0xAE, 0x20, 0x00, 0x40, 0xA1, 0xC8, 0xA8, 0x3F, 0xD3, 0x00,
            0xD5, 0x80, 0xD9, 0xF1, 0xDA, 0x12, 0xDB, 0x40, 0x8D, 0x14, 0xAF):
            self.write_cmd(cmd)
        self.fill(0)
        self.show()

    def show(self):
        self.write_cmd(0x21); self.write_cmd(0); self.write_cmd(self.width - 1)
        self.write_cmd(0x22); self.write_cmd(0); self.write_cmd(self.height // 8 - 1)
        self.i2c.writeto(self.addr, b'\x40' + self.buffer)

    def fill(self, c): self.fb.fill(c)
    def text(self, s, x, y): self.fb.text(s, x, y)
    def pixel(self, x, y, c): self.fb.pixel(x, y, c)
    def rect(self, x, y, w, h, c): self.fb.rect(x, y, w, h, c)
    def fill_rect(self, x, y, w, h, c): self.fb.fill_rect(x, y, w, h, c)

class SSD1306I2C(SSD1306):
    pass

# Definiciond de la funcion antirebore
class BotonSimple:
    def __init__(self, pin, reboteMs=50):
        self.pin = pin
        self.reboteMs = reboteMs
        self.ultimoEstado = True
        self.ultimoCambio = 0
    
    def estaPresionado(self):
        actual = self.pin.value()
        ahora = time.ticks_ms()
        if actual != self.ultimoEstado:
            if time.ticks_diff(ahora, self.ultimoCambio) > self.reboteMs:
                self.ultimoEstado = actual
                self.ultimoCambio = ahora
                return actual == 0
        return False

# ----------------------------
# CONFIGURACIÓN HARDWARE
# ----------------------------
print("Inicializando juego...")

# Pantalla OLED
try:
    i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
    oled = SSD1306I2C(128, 64, i2c)
    print("Pantalla OLED detectada")
except Exception as e:
    print("Error: Verifica conexión OLED en SCL=22 y SDA=21")

# Botones
botonArriba = BotonSimple(Pin(32, Pin.IN, Pin.PULL_UP))
botonAbajo = BotonSimple(Pin(33, Pin.IN, Pin.PULL_UP))
botonIzquierda = BotonSimple(Pin(27, Pin.IN, Pin.PULL_UP))
botonDerecha = BotonSimple(Pin(14, Pin.IN, Pin.PULL_UP))
botonInicio = BotonSimple(Pin(25, Pin.IN, Pin.PULL_UP))

# Buzzer
buzzer = PWM(Pin(26), freq=1000, duty=0)

#Funcion para que suene en cada movimientp
def pitido(freq=1000, duracion=80):
    buzzer.freq(freq)
    buzzer.duty(512)
    time.sleep_ms(duracion)
    buzzer.duty(0)

#Definicion de los romos que hará en buzzer en el game over
def melodia_game_over():
    tonos = [(392, 200), (330, 200), (262, 400)]
    for f, d in tonos:
        buzzer.freq(f)
        buzzer.duty(512)
        time.sleep_ms(d)
    buzzer.duty(0)

#Variables que son constantes en el juego
ESTADO_MENU = 0
ESTADO_JUEGO = 1
ESTADO_PAUSA = 2
ESTADO_FIN = 3

#Variables globales 
estado = ESTADO_MENU
modo = 0 #Para la seleccion del modo de juego
CELDA = 2 # el tamaño por pixel del juego es 2x2
MAXX = 128 #dimensiones de la pantalla
MAXY = 64

#Estado de posición inicial de la culebra
def iniciarSerpiente():
    return [(40,30),(38,30),(36,30)]

#Configuración de variables (Inicialización)
serpiente = iniciarSerpiente()
direccion = (2,0)
comida = (60,30)
puntaje = 0
inicioJuego = 0
duracionJuego = 60
ultimoMovimiento = time.ticks_ms()
intervaloVelocidad = 200
ultimoAumentoDificultad = time.ticks_ms()

#Funcion para que se defina una posición de comida en cada ronda (Random)
def posicionComidaAleatoria():
    while True:
        x = urandom.randint(0, (MAXX//2)-1) * 2
        y = urandom.randint(5, (MAXY//2)-1) * 2
        if (x,y) not in serpiente and y >= 10:
            return (x,y)

#Grenara la comida en la posición definida por la variable anterior actiallizando la variable comida
def generarComida():
    global comida
    comida = posicionComidaAleatoria()

#Dibujar en la pantalla el puntaje y todo lo que hay alrededor del juego dirante el juego
def dibujarHud():
    oled.text("Puntos:{}".format(puntaje), 0, 0) #Puntaje que se actualiza
    if modo == 1:
        transcurrido = (time.ticks_ms() - inicioJuego) // 1000
        restante = max(0, duracionJuego - transcurrido)
        oled.text("Tiempo:{}".format(restante), 80, 0) #Tiempo que se actualiza

#Dibula la sepiente en 2x2
def dibujarSerpiente():
    for parte in serpiente:
        oled.fill_rect(parte[0], parte[1], 2, 2, 1)

#Dibula la comida en 2x2
def dibujarComida():
    oled.fill_rect(comida[0], comida[1], 2, 2, 1)

def moverSerpiente():
    global serpiente, puntaje
    cabezaX, cabezaY = serpiente[0]
    dx, dy = direccion
    nuevaCabeza = (cabezaX + dx, cabezaY + dy) #Calcula la nueva posicion de la cabeza

    if nuevaCabeza[0] < 0 or nuevaCabeza[0] >= MAXX or nuevaCabeza[1] < 10 or nuevaCabeza[1] >= MAXY: 
        return False #Verifica si la nueva cabeza choca con los bordes de la pantalla o con la
    if nuevaCabeza in serpiente:
        return False

    serpiente.insert(0, nuevaCabeza)
    if nuevaCabeza == comida: #Verifica que la caveza coincida con la posicion de la comida para aumental el puntaje y modificar el tamaño
        puntaje += 10 #Suma 10 puntos
        pitido(1500, 60) #Suena
        generarComida()
    else:
        serpiente.pop()
    return True

def establecerParametrosModo(): #Lo que hace cada modo de juego específico
    global intervaloVelocidad, duracionJuego
    if modo == 0:  # Clasico
        intervaloVelocidad = 200
        duracionJuego = 9999  # sin límite real
    elif modo == 1:  # Contra tiempo
        intervaloVelocidad = 110  # más rápido
        duracionJuego = 60  # solo 30 segundos
    else:  # Hardcore
        intervaloVelocidad = 50 # muy rápido
        duracionJuego = 9999  # sin límite

def reiniciarJuego(): #Reinicia el juego (Para cuando se termine)
    global serpiente, direccion, puntaje, comida, inicioJuego, ultimoMovimiento, ultimoAumentoDificultad
    serpiente = iniciarSerpiente()
    direccion = (2,0)
    puntaje = 0
    generarComida()
    inicioJuego = time.ticks_ms()
    ultimoMovimiento = time.ticks_ms()
    ultimoAumentoDificultad = time.ticks_ms()
    establecerParametrosModo()

#Inicializacion del juego con las funciones del modo inicial
establecerParametrosModo()
generarComida()

#Ciclo principal que ejecuta todas las funciones
while True:
    oled.fill(0) #limpia la pantalla en cada iteración para redibujar el contenido.

    if estado == ESTADO_MENU: #Esto es cuando esta em el menu
        oled.text("SNAKE", 46, 0)
        y0 = 20
        for i, nombre in enumerate(("Clasico","Contra-T","Hardcore")):
            prefijo = ">" if i == modo else " "
            oled.text("{} {}".format(prefijo, nombre), 20, y0 + i*10)
        oled.text("Inicio para jugar", 0, 56)

        if botonArriba.estaPresionado():
            modo = (modo - 1) % 3
            pitido(800, 80)
        if botonAbajo.estaPresionado():
            modo = (modo + 1) % 3
            pitido(800, 80)
        if botonInicio.estaPresionado():
            estado = ESTADO_JUEGO
            reiniciarJuego()
            pitido(1200, 100)

    elif estado == ESTADO_JUEGO: #Si no, es porque esta en estado juefo
        cambioDireccion = False
        if botonArriba.estaPresionado() and direccion != (0,2): #Cambia de dirección 2 pixeles segun boton presionado
            direccion = (0,-2); cambioDireccion = True
        elif botonAbajo.estaPresionado() and direccion != (0,-2):
            direccion = (0,2); cambioDireccion = True
        elif botonIzquierda.estaPresionado() and direccion != (2,0):
            direccion = (-2,0); cambioDireccion = True
        elif botonDerecha.estaPresionado() and direccion != (-2,0):
            direccion = (2,0); cambioDireccion = True

        if cambioDireccion: #Ejecuta el cambio
            if not moverSerpiente():
                melodia_game_over()
                estado = ESTADO_FIN

        if botonInicio.estaPresionado(): #Pausamos el juego
            estado = ESTADO_PAUSA
            pitido(1000, 80)

        ahora = time.ticks_ms()
        if time.ticks_diff(ahora, ultimoMovimiento) > intervaloVelocidad:
            if not moverSerpiente():
                melodia_game_over()
                estado = ESTADO_FIN
            ultimoMovimiento = ahora

        dibujarSerpiente()
        dibujarComida()
        dibujarHud()

        if modo == 1:
            transcurrido = (time.ticks_ms() - inicioJuego) // 1000
            if transcurrido >= duracionJuego:
                melodia_game_over()
                estado = ESTADO_FIN

    elif estado == ESTADO_PAUSA:
        oled.text("PAUSA", 52, 28)
        oled.text("Inicio->continuar", 0, 56)
        if botonInicio.estaPresionado():
            estado = ESTADO_JUEGO
            pitido(1200, 100)

    elif estado == ESTADO_FIN:
        oled.text("GAME OVER", 28, 16)
        oled.text("Puntos: {}".format(puntaje), 36, 32)
        oled.text("Inicio->Menu", 24, 52)
        if botonInicio.estaPresionado():
            estado = ESTADO_MENU
            pitido(600, 120)

    oled.show()
    time.sleep_ms(20)