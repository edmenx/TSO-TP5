"""
UNJu - Facultad de Ingeniería
Teoría de Sistemas Operativos (TSO) - Ciclo Lectivo 2026
Cátedra: Ing. María Fernanda Vázquez - JTP: Ing. Fabio D. Argañaraz

Ejercicio Práctico N° 2: El Problema del Oso y las Abejas
Bibliografía de Referencia:
- Silberschatz: Cap. 6.6 (Problemas clásicos de sincronización)
- Stallings: Cap. 5.4 (Sincronización con semáforos)
"""

import sys
import threading
import time
import random

# Configuración UTF-8 para consola Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

M = 10                  # Capacidad del tarro de miel
NUM_ABEJAS = 5          # Número de abejas obreras
tarro_miel = 0          # Variable compartida
simulacion_activa = True

# TODO PARA EL ESTUDIANTE:
# 1. Define los mecanismos de sincronización necesarios:
# - Un cerrojo (Lock) o semáforo binario para exclusión mutua en el tarro.
# - Un semáforo para despertar al oso cuando el tarro esté lleno.
# - Un semáforo para que las abejas esperen si el tarro está lleno o el oso está comiendo.
mutex = threading.Lock()
sem_oso = threading.Semaphore(0)
sem_tarro_disponible = threading.Semaphore(1) # Permiso de llenado para las abejas

def abeja(id_abeja):
  global tarro_miel, simulacion_activa
  while simulacion_activa:
    time.sleep(random.uniform(0.05, 0.2))

    if not simulacion_activa:
      break

    # 1. Esperar a que el tarro esté disponible y no lleno/bloqueado
    sem_tarro_disponible.acquire()

    if not simulacion_activa:
      sem_tarro_disponible.release()
      break

    # 2. Entrar en exclusión mutua para manipular el recurso compartido
    with mutex:
      # 3. Depositar una porción de miel
      tarro_miel += 1
      print(f"🐝 Abeja {id_abeja} depositó miel -> Tarro: {tarro_miel}/{M}")

      # 4. Verificar si se completó la capacidad
      if tarro_miel == M:
        print(f"🚨 [Tarro Lleno] Abeja {id_abeja} despierta al oso dormido!")
        sem_oso.release()
      else:
        # 5. Si no está lleno, permitir que la siguiente abeja deposite
        sem_tarro_disponible.release()

def oso(max_tarros=2):
  global tarro_miel, simulacion_activa
  tarros_comidos = 0
  while tarros_comidos < max_tarros:
    # Espera pasiva (bloqueo) hasta que una abeja señale que el tarro está lleno
    sem_oso.acquire()

    print("\n🐻 El oso se despierta y se come toda la miel!")
    with mutex:
      tarro_miel = 0
    print("🐻 El oso vuelve a dormir plácidamente.\n")

    tarros_comidos += 1
    time.sleep(0.1)

    # Avisar que el tarro está vacío y disponible para continuar produciendo
    sem_tarro_disponible.release()

  simulacion_activa = False


if __name__ == "__main__":
  print("=" * 60)
  print(" Iniciando Simulación: El Oso y las Abejas (UNJu FI)")
  print("=" * 60)

  hilo_oso = threading.Thread(target=oso, args=(2,))
  hilos_abejas = [
      threading.Thread(target=abeja, args=(i + 1,), daemon=True)
      for i in range(NUM_ABEJAS)
  ]

  hilo_oso.start()
  for h in hilos_abejas:
    h.start()

  hilo_oso.join()

  print("=" * 60)
  print(" Simulación finalizada exitosamente.")
  print("=" * 60)

