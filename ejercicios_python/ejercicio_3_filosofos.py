"""
UNJu - Facultad de Ingeniería
Teoría de Sistemas Operativos (TSO) - Ciclo Lectivo 2026
Cátedra: Ing. María Fernanda Vázquez - JTP: Ing. Fabio D. Argañaraz

Ejercicio Práctico N° 3: La Cena de los Filósofos (Prevención de Deadlock)
Bibliografía de Referencia:
- Silberschatz: Cap. 6.6 (Problemas clásicos de sincronización)
- Stallings: Cap. 5.6 (Problema de los filósofos comensales)
"""

import threading
import time
import random

NUM_FILOSOFOS = 5
# Cada tenedor está representado por un Lock (exclusión mutua)
tenedores = [threading.Lock() for _ in range(NUM_FILOSOFOS)]

# Variable para contar cuántas veces comió cada filósofo
comidas = [0] * NUM_FILOSOFOS
lock_print = threading.Lock()

def log(msg):
    with lock_print:
        print(msg)

def pensar(id):
    log(f"🤔 Filósofo {id} está pensando...")
    time.sleep(random.uniform(0.1, 0.3))

def comer(id):
    log(f"🍝 Filósofo {id} está comiendo espagueti...")
    comidas[id] += 1
    time.sleep(random.uniform(0.1, 0.3))
    log(f"✨ Filósofo {id} terminó de comer (total comidas: {comidas[id]}).")

def filosofo(id, rondas=3):
    """
    Representa el ciclo de vida de un filósofo: pensar -> tomar tenedores -> comer -> soltar tenedores.
    
    CONSIGNA:
    Si todos los filósofos toman primero su tenedor izquierdo y luego el derecho:
        izq = id
        der = (id + 1) % NUM_FILOSOFOS
    se produce un DEADLOCK (interbloqueo) si todos toman su tenedor izquierdo simultáneamente.
    
    TODO PARA EL ESTUDIANTE:
    Implementa una solución para prevenir el Deadlock rompiendo una de las condiciones de Coffman
    (por ejemplo, la 'Espera Circular' usando una estrategia asimétrica):
    - Si el filósofo es el último (id == NUM_FILOSOFOS - 1) o es impar, que tome primero el tenedor
      DERECHO y luego el IZQUIERDO.
    - Los demás filósofos toman primero el IZQUIERDO y luego el DERECHO.
    - Alternativamente, puedes usar un semáforo contador (árbitro/mozo) que permita un máximo de 4 comensales.
    """
    for _ in range(rondas):
        pensar(id)
        
        # Identificadores de los tenedores adyacentes
        tenedor_izq = id
        tenedor_der = (id + 1) % NUM_FILOSOFOS
        
        # =========================================================================
        # INICIO TODO: Implementar adquisición y liberación segura de tenedores
        # =========================================================================
        
        # PISTA DE IMPLEMENTACIÓN ASIMÉTRICA:
        # =========================================================================
    # ESTRATEGIA ASIMÉTRICA DE ASIGNACIÓN 
    # =========================================================================
    # El filósofo N-1 invierte el orden de solicitud respecto a sus pares.
    # Esto impide la formación de un ciclo cerrado en el grafo de asignación.
        if id == NUM_FILOSOFOS - 1:
            primero = tenedor_der
            segundo = tenedor_izq
        else:
            primero = tenedor_izq
            segundo = tenedor_der

    # Adquisición ordenada bajo exclusión mutua
        with tenedores[primero]:
            with tenedores[segundo]:
             comer(id)
    # Los tenedores se liberan automáticamente en orden inverso al salir de los bloques 'with'
                
        # =========================================================================
        # FIN TODO
        # =========================================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" Iniciando Simulación de los Filósofos Comensales (UNJu FI)")
    print("=" * 60)
    
    hilos = []
    for i in range(NUM_FILOSOFOS):
        t = threading.Thread(target=filosofo, args=(i, 3), name=f"Filosofo-{i}")
        hilos.append(t)
        t.start()
        
    for t in hilos:
        t.join()
        
    print("=" * 60)
    print(" Resumen de Comidas:")
    for i, c in enumerate(comidas):
        print(f" - Filósofo {i}: {c} veces comió.")
    print(" ¡Simulación completada sin Interbloqueo (Deadlock)!")
    print("=" * 60)
