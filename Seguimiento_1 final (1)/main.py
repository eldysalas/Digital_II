from machine import Pin, mem32
import time, random

GPIO_OUT_REG = const(0x03FF44004)

# Configuración de salidas
Pin(15, Pin.OUT)   
Pin(4, Pin.OUT)    
Pin(5, Pin.OUT)   
Pin(18, Pin.OUT)   
LedRojo  = 0b1000000000000000     # Pin 15 
LedAzul  = 0b10000                # Pin 4 
LedVerde = 0b100000               # Pin 5 
Buzzer   = 0b1000000000000000000  # Pin 18 

# Botones jugador A 
bA1 = Pin(12, Pin.IN, Pin.PULL_DOWN)
bA2 = Pin(13, Pin.IN, Pin.PULL_DOWN)
bA3 = Pin(14, Pin.IN, Pin.PULL_DOWN)
bA4 = Pin(27, Pin.IN, Pin.PULL_DOWN)

# Botones jugador B 
bB1 = Pin(19, Pin.IN, Pin.PULL_DOWN)
bB2 = Pin(21, Pin.IN, Pin.PULL_DOWN)
bB3 = Pin(22, Pin.IN, Pin.PULL_DOWN)
bB4 = Pin(23, Pin.IN, Pin.PULL_DOWN)

# Botones del juego gneral
Start = Pin(25, Pin.IN, Pin.PULL_DOWN)        
Interrupcion = Pin(26, Pin.IN, Pin.PULL_DOWN) 
Stop = Pin(33, Pin.IN, Pin.PULL_DOWN)         

Extraactivar = False #Nuestra bandera para el extra

# Variables globales de resultado
puntajeA = 0
puntajeB = 0
ronda = 1
Modojuego = True
jugadores = 1

# Funciones

#Activar bandera para ingresar al modo extra
def Modoextra(pin):
    global Extraactivar
    Extraactivar = True
    print ("Acabas de activar el modo extra")

Interrupcion.irq(trigger=Pin.IRQ_RISING, handler=Modoextra)

def estadoApagado():
    mem32[GPIO_OUT_REG] = 0b0

def antirrebote(boton): #Antirrebote de jugadores
    if boton.value() == 1:
        time.sleep_ms(50)
        if boton.value() == 1:
            return True
    return False

def antirrebote_control(boton): #de botones de juego
    if boton.value() == 1:
        time.sleep_ms(50)
        if boton.value() == 1:
            while boton.value() == 1:
                time.sleep_ms(10)
            return True
    return False

def cantidadJugadores():
    global jugadores    
    print("Juego de medición de reflejos")
    print("-"*40)

    while True:
        try:
            numerojugadores = input("¿Cuantos jugadores estarán? (1 o 2): ")
            if numerojugadores == "1":
                jugadores = 1
                print(f"Seleccionó: {jugadores} jugador")
                break   
            elif numerojugadores == "2":
                jugadores = 2
                print(f"Seleccionó: {jugadores} jugadores")
                break
            else:
                print("La opción no es válida")       
        except:
            print("Error")

# reaccion y recopilación de la misma
def reaccion(correctoA, correctoB):
    inicio = time.ticks_ms()
    while True:
        if Stop.value() == 1:
            estadoApagado()
            return "salir", None, None

        if Extraactivar:
            return None, None, "extra"
        
        for b in [bA1, bA2, bA3, bA4]:
            if antirrebote(b):
                fin = time.ticks_ms()
                tiempo = time.ticks_diff(fin, inicio)
                correcto = (b == correctoA)
                return "A", tiempo, correcto

        if jugadores == 2:
            for b in [bB1, bB2, bB3, bB4]:
                if antirrebote(b):
                    fin = time.ticks_ms()
                    tiempo = time.ticks_diff(fin, inicio)
                    correcto = (b == correctoB)
                    return "B", tiempo, correcto

# ---------------- JUEGO NORMAL ----------------

def modo1():
    global puntajeA, puntajeB, Modojuego, ronda
    estimulos = [
        (LedRojo, bA1, bB1, "Rojo"),     
        (LedAzul, bA2, bB2, "Azul"),     
        (LedVerde, bA3, bB3, "Verde"),
        (Buzzer, bA4, bB4, "Sonido")
    ]

    while Modojuego:
        if Extraactivar:
            break
        
        print(f'Ronda: {ronda}')
        estadoApagado()
        
        if Stop.value() == 1:
            Modojuego = False
            break
        
        espera = random.randint(1, 10)
        for i in range(espera * 10):
            if Extraactivar:
                break
            if Stop.value() == 1:
                Modojuego = False
                return
            time.sleep_ms(100)
        
        if Extraactivar:
            break

        salida, botonA, botonB, nombre = random.choice(estimulos)
        mem32[GPIO_OUT_REG] = salida
        print(f"Estímulo: {nombre}")
        time.sleep(0.5)   # tiempo encendido
        estadoApagado()   # se apaga antes de esperar reacción

        jugador, tiempo, correcto = reaccion(botonA, botonB)
        
        if jugador == "salir":
            Modojuego = False
            break
        
        if jugador is None and tiempo is None and correcto == "extra":
            break
            
        if jugador == "A": 
            if correcto:
                puntajeA += 1
                print(f"Jugador A: CORRECTO en {tiempo} ms (+1 punto)")
            else:     
                puntajeA -= 1
                print(f"Jugador A: INCORRECTO, pierde un punto")

        elif jugador == "B":
            if correcto:
                puntajeB += 1
                print(f"Jugador B: CORRECTO en {tiempo} ms (+1 punto)")
            else:     
                puntajeB -= 1
                print(f"Jugador B: INCORRECTO, pierde un punto")

        print(f"Puntaje A: {puntajeA}")
        if jugadores == 2:
            print(f"Puntaje B: {puntajeB}")
        else:
            print()

        estadoApagado()
        ronda += 1
        time.sleep(1)

# ---------------- MODO EXTRA ----------------

def extra():
    global puntajeA, puntajeB, Extraactivar

    print("\n***Ingresaste al modo extra del juego***")
    print("Observa la secuencia de estímulos...")
    print("Cuando veas/escuches TODOS los estímulos AL MISMO TIEMPO, presiona cualquier botón")
    
    estadoApagado()
    time.sleep(2)

    estimulos_info = [
        (LedRojo, "LED ROJO"),
        (LedAzul, "LED AZUL"), 
        (LedVerde, "LED VERDE"),
        (Buzzer, "BUZZER")
    ]
    
    print("Secuencia de estímulos:")
    for salida, nombre in estimulos_info:
        print(f"- {nombre}")
        mem32[GPIO_OUT_REG] = salida
        time.sleep(0.8)
        estadoApagado()
        time.sleep(0.4)
    
    print("¡Ahora todos juntos! ¡PRESIONA CUALQUIER BOTÓN AHORA!")
    mem32[GPIO_OUT_REG] = LedRojo | LedAzul | LedVerde | Buzzer
    
    inicio = time.ticks_ms()
    jugador_respondio = None
    tiempo_respuesta = None
    
    while True:
        if Stop.value() == 1:
            print("Modo extra cancelado")
            estadoApagado()
            Extraactivar = False
            return

        for boton in [bA1, bA2, bA3, bA4]:
            if antirrebote(boton):
                fin = time.ticks_ms()
                tiempo_respuesta = time.ticks_diff(fin, inicio)
                jugador_respondio = "A"
                break
        
        if jugador_respondio:
            break
            
        if jugadores == 2:
            for boton in [bB1, bB2, bB3, bB4]:
                if antirrebote(boton):
                    fin = time.ticks_ms()
                    tiempo_respuesta = time.ticks_diff(fin, inicio)
                    jugador_respondio = "B"
                    break
        
        if jugador_respondio:
            break
            
        if time.ticks_diff(time.ticks_ms(), inicio) > 10000:
            print("Tiempo agotado en modo extra")
            break

    if jugador_respondio and tiempo_respuesta:
        if jugador_respondio == "A":
            puntajeA += 3  
            print(f"¡Jugador A: Secuencia completada en {tiempo_respuesta} ms (+3 puntos extra)!")
        elif jugador_respondio == "B":
            puntajeB += 3  
            print(f"¡Jugador B: Secuencia completada en {tiempo_respuesta} ms (+3 puntos extra)!")
    else:
        print("Nadie respondió a tiempo")

    print(f"\nPuntaje A: {puntajeA}")
    if jugadores == 2:
        print(f"Puntaje B: {puntajeB}")
    
    estadoApagado()
    time.sleep(2)
    Extraactivar = False
    print("Termina modo extra")

# programa main

print("Sistema de reflejos iniciado")
cantidadJugadores() 
print("Presione start")

while True: 
    if Start.value() == 1:
        time.sleep_ms(200) 
        print("¡Juego iniciado!") 
        break    

while Modojuego:
    if Extraactivar:  
        extra()
    else:     
        modo1()

print("JUEGO FINALIZADO")
print(f"Puntaje final A: {puntajeA}")

if jugadores == 2:
    print(f"Puntaje final B: {puntajeB}")
    if puntajeA > puntajeB:
        print("Ganador: Jugador A")
    elif puntajeB > puntajeA:
        print("Ganador: Jugador B")
    else:
        print("Empate")
else:
    print(f"Puntaje final: {puntajeA}")
