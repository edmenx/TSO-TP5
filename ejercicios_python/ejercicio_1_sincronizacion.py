"""
UNJu - Facultad de Ingeniería
Teoría de Sistemas Operativos (TSO) - Ciclo Lectivo 2026
Cátedra: Ing. María Fernanda Vázquez - JTP: Ing. Fabio D. Argañaraz

Ejercicio Práctico N° 1: Sincronización Básica y Trazas de Señalización
Bibliografía de Referencia:
- Silberschatz: Cap. 6.2 y 6.6
- Guía Histórica TP5 (2025): Ejercicio 1 de Comprensión y Problema 2 de Secuencias
"""

import sys
import threading
import time

# Configuración UTF-8 para consola Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ============================================================================
# PARTE 1: Exclusión Mutua y Ordenamiento sobre Variable Compartida
# ============================================================================
# Consigna (TP 2025 - Comprensión 1):
# Sincronizar A y B de tal manera que SIEMPRE el resultado de la ejecución sea
# X = 50 en la división y X = 200 en el incremento (o viceversa según el orden lógico).
# Determina qué semáforo o lock se necesita y su valor inicial.

X = 199

# PARA EL ESTUDIANTE:
# 1. Define los mecanismos de sincronización necesarios:
sem_A = threading.Semaphore(1)  # A arranca con permiso
sem_B = threading.Semaphore(0)  # B espera a que A termine

def proceso_A():
    global X

    X = X + 1
    print(f"[Parte 1] Proceso A: X = {X}")
   

def proceso_B():
    global X
    # Se prodria ajusta a // 4 para dar exactamente 50 (200 // 4 = 50)
    X = X // 10
    print(f"[Parte 1] Proceso B: X = {X}")
    


# ============================================================================
# PARTE 2: Sincronización de Trazas Estrictas (Secuencia ABCABC)
# ============================================================================
# Consigna (TP 2025 - Problema 2):
# Dados tres procesos concurrentes A, B y C, utilizar semáforos de señalización
# para forzar de forma determinista la secuencia estricta: A -> B -> C -> A -> B -> C...
#
# Pista pedagógica: Recuerda que un semáforo inicializado en 0 actúa como un "evento"
# o "señal" de sincronización (un hilo espera con acquire() hasta que otro hilo hace release()).

# TODO PARA EL ESTUDIANTE:
# Define con qué valor inicial deben comenzar los semáforos para que 'A' arranque primero:
sem_sig_A = threading.Semaphore(1)  # Arranca Primero
sem_sig_B = threading.Semaphore(0)  # Espera turno tras A
sem_sig_C = threading.Semaphore(0)  # Espera turno tras B

def proceso_emisor_A(rondas=3):
    for i in range(rondas):
        sem_sig_A.acquire()
        print(f"[Parte 2] Ronda {i+1} -> 🅰️ Proceso A ejecutando")
        time.sleep(0.1)
        sem_sig_B.release()

def proceso_receptor_B(rondas=3):
    for i in range(rondas):
        sem_sig_B.acquire()
        print(f"[Parte 2] Ronda {i+1} -> 🅱️ Proceso B ejecutando")
        time.sleep(0.1)
        sem_sig_C.release()

def proceso_receptor_C(rondas=3):
    for i in range(rondas):
        sem_sig_C.acquire()
        print(f"[Parte 2] Ronda {i+1} -> 🅲 Proceso C ejecutando")
        time.sleep(0.1)
        sem_sig_A.release()


if __name__ == "__main__":
    print("=" * 60)
    print("EJERCICIO 1 - PARTE 1: Variable Compartida")
    print("=" * 60)
    hA = threading.Thread(target=proceso_A)
    hB = threading.Thread(target=proceso_B)
    hA.start(); hB.start()
    hA.join(); hB.join()

    print("\n" + "=" * 60)
    print("EJERCICIO 1 - PARTE 2: Secuencia Estricta ABCABC")
    print("=" * 60)
    tA = threading.Thread(target=proceso_emisor_A)
    tB = threading.Thread(target=proceso_receptor_B)
    tC = threading.Thread(target=proceso_receptor_C)
    tA.start(); tB.start(); tC.start()
    tA.join(); tB.join(); tC.join()
    pass
