from machine import Pin, ADC, PWM
import time

# Definicion de servos
servobase = PWM(Pin(14), freq=50)  #Base de la grua
servobrazo = PWM(Pin(27), freq=50)

DUTYMIN = 26 
DUTYMAX = 128 

# Funcion para los angulos del servo
def maprange(x, inmin, inmax, outmin, outmax):
    return int((x - inmin) * (outmax - outmin) / (inmax - inmin) + outmin)

# Funcion para mover el servo
def moverservo(servo, angulo):
    angulo = max(0, min(180, angulo))
    duty = maprange(angulo, 0, 180, DUTYMIN, DUTYMAX)
    servo.duty(duty)

# Potenciometros y pulsadores
# Potenciometro base: 12 bits
base = ADC(Pin(34))
base.atten(ADC.ATTN_11DB)
base.width(ADC.WIDTH_12BIT)

# Potenciometro brazo: 10 bits
brazo = ADC(Pin(35))
brazo.atten(ADC.ATTN_11DB)
brazo.width(ADC.WIDTH_10BIT)

# Pulsadores 
retorno = Pin(25, Pin.IN, Pin.PULL_UP)
rutina = Pin(26, Pin.IN, Pin.PULL_UP)

# Pines de salida
ledrojo = Pin(15, Pin.OUT)
ledverde = Pin(4, Pin.OUT)
buzzer = Pin(18, Pin.OUT)

def estadoledsbuzzer(rojo=False, verde=False, buzzeron=False): # Funcion para cambiar de estado con banderas
    if rojo == True:
        ledrojo.value(1)
    else:
        ledrojo.value(0)
    
    if verde == True:
        ledverde.value(1)
    else:
        ledverde.value(0)
    
    if buzzeron == True:
        buzzer.value(1)
    else:
        buzzer.value(0)

# Variables globales
retornoflag = False
rutinaflag = False
posicionactualbase = 90
posicionactualbrazo = 45
modoautomatico = False

# Variables antirrebote
ultimotiempretorno = 0
ultimotiemprutina = 0
DEBOUNCETIME = 50  # Reducido a 50 ms para mejor responsividad

# Manejadores de interrupciones
def manejadorretorno(pin):
    global retornoflag, ultimotiempretorno
    tiempoactual = time.ticks_ms()
    if time.ticks_diff(tiempoactual, ultimotiempretorno) > DEBOUNCETIME:
        print(f"Interrupcion: Boton retorno (Pin {pin}) presionado, estado={pin.value()}")
        retornoflag = True
        ultimotiempretorno = tiempoactual

def manejadorrutina(pin):
    global rutinaflag, ultimotiemprutina
    tiempoactual = time.ticks_ms()
    if time.ticks_diff(tiempoactual, ultimotiemprutina) > DEBOUNCETIME:
        print(f"Interrupcion: Boton rutina (Pin {pin}) presionado, estado={pin.value()}")
        rutinaflag = True
        ultimotiemprutina = tiempoactual

# Modo manual
def modomanualcontrol():
    global posicionactualbase, posicionactualbrazo
    
    if modoautomatico == False:
        estadoledsbuzzer(rojo=False, verde=True, buzzeron=False)
        
        # Leer potenciometros
        lecturabase = base.read()
        angbase = maprange(lecturabase, 0, 4095, 0, 180)
        
        lecturabrazo = brazo.read()
        angbrazo = maprange(lecturabrazo, 0, 1023, 0, 180)
        
        # Mover servos
        moverservo(servobase, angbase)
        moverservo(servobrazo, angbrazo)
        
        # Actualizar posiciones
        posicionactualbase = angbase
        posicionactualbrazo = angbrazo

# Retorno automatico
def retornoautomatico():
    global modoautomatico, posicionactualbase, posicionactualbrazo
    
    modoautomatico = True
    print("Iniciando retorno automatico...")
    
    estadoledsbuzzer(rojo=True, verde=False, buzzeron=True)
    
    # Posiciones objetivo
    posinicialbase = 90
    posinicialbrazo = 45
    
    # Calcular pasos
    pasos = 30
    pasobase = (posinicialbase - posicionactualbase) / pasos
    pasobrazo = (posinicialbrazo - posicionactualbrazo) / pasos
    
    # Movimiento gradual
    for i in range(pasos + 1):
        angbase = int(posicionactualbase + pasobase * i)
        angbrazo = int(posicionactualbrazo + pasobrazo * i)
        
        angbase = max(0, min(180, angbase))
        angbrazo = max(0, min(180, angbrazo))
        
        moverservo(servobase, angbase)
        moverservo(servobrazo, angbrazo)
        time.sleep(0.05)
        
        if i % 5 == 0:
            estadoledsbuzzer(rojo=True, verde=False, buzzeron=not buzzer.value())
    
    # Actualizar posiciones finales
    posicionactualbase = posinicialbase
    posicionactualbrazo = posinicialbrazo
    
    print("Ya estas en la posición inicial")
    estadoledsbuzzer(rojo=True, verde=False, buzzeron=False)
    time.sleep(1)
    
    modoautomatico = False

# Rutina predefinida
def rutinapredefinida():
    global modoautomatico, posicionactualbase, posicionactualbrazo
    
    modoautomatico = True
    print("Entraste a la rutina")
    
    estadoledsbuzzer(rojo=True, verde=False, buzzeron=True)
    
    secuencia = [
        (90, 45),   # Inicio paso1
        (30, 90),   # Izquierda arriba
        (30, 120),  # Izquierda mas arriba
        (150, 120), # Derecha arriba
        (150, 60),  # Derecha medio
        (150, 30),  # Derecha abajo
        (90, 45),   # Retorno
    ]
    
    for i, (angbaseobjetivo, angbrazoobjetivo) in enumerate(secuencia):
        print(f"Paso {i+1}: Base={angbaseobjetivo}°, Brazo={angbrazoobjetivo}°")
        
        # Movimiento gradual
        pasosmovimiento = 15
        iniciobase = posicionactualbase
        iniciobrazo = posicionactualbrazo
        
        for j in range(pasosmovimiento + 1):
            factor = j / pasosmovimiento
            angbase = int(iniciobase + (angbaseobjetivo - iniciobase) * factor)
            angbrazo = int(iniciobrazo + (angbrazoobjetivo - iniciobrazo) * factor)
            
            moverservo(servobase, angbase)
            moverservo(servobrazo, angbrazo)
            time.sleep(0.05)
        
        posicionactualbase = angbaseobjetivo
        posicionactualbrazo = angbrazoobjetivo
        
        # Pausa entre pasos
        for i in range(6):
            estadoledsbuzzer(rojo=True, verde=False, buzzeron=(i % 2 == 0))
            time.sleep(0.25)
    
    print("Rutina completada")
    estadoledsbuzzer(rojo=True, verde=False, buzzeron=False)
    time.sleep(1)
    
    modoautomatico = False

# Esto es cuando iniciamos a correr el código
def inicializarsistema():
    global posicionactualbase, posicionactualbrazo
    
    print("SISTEMA DE GRUA")
    
    # Configurar interrupciones en los botones
    retorno.irq(trigger=Pin.IRQ_FALLING, handler=manejadorretorno)
    rutina.irq(trigger=Pin.IRQ_FALLING, handler=manejadorrutina)
    
    # Posicion inicial
    moverservo(servobase, 90)
    moverservo(servobrazo, 45)
    
    posicionactualbase = 90
    posicionactualbrazo = 45
    
    estadoledsbuzzer(rojo=False, verde=True, buzzeron=False)
    
    print("Sistema iniciado en Modo manual")


# Sistema principal
inicializarsistema()

while True:
    try:
        if retornoflag == True:
            print("retorno")
            retornoautomatico()
            retornoflag = False
            print("Estas en modo manual")
            
        if rutinaflag == True:
            print("modo rutima")
            rutinapredefinida()
            rutinaflag = False 
            print("Estas en modo manual")
            
        if retornoflag == False and rutinaflag == False:
            modomanualcontrol()
        
        time.sleep(0.01) 
        
    except KeyboardInterrupt:
        estadoledsbuzzer(rojo=False, verde=False, buzzeron=False)
        break