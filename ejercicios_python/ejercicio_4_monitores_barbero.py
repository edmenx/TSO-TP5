"""
UNJu - Facultad de Ingeniería
Teoría de Sistemas Operativos (TSO) - Ciclo Lectivo 2026
Cátedra: Ing. María Fernanda Vázquez - JTP: Ing. Fabio D. Argañaraz

Ejercicio Práctico N° 4: Monitores y Variables de Condición (El Barbero Dormilón)
Bibliografía de Referencia:
- Silberschatz: Cap. 6.7 (Monitores) y Cap. 6.6 (El problema del barbero dormilón)
- Diapositivas U5: Diapositiva 20 a 24 (Monitores y Problemas Clásicos)

Fundamentos de Monitores:
Un Monitor provee exclusión mutua automática sobre sus variables internas mediante un cerrojo (Lock).
Para coordinar eventos disjuntos, utiliza Variables de Condición separadas:
1. 'cond_barbero': Para que el barbero espere a los clientes o su acomodo en el sillón.
2. 'cond_sala_espera': Para que los clientes esperen hasta que el sillón quede libre.
3. 'cond_corte': Para que el cliente en el sillón espere a que el barbero termine de cortar.
"""

import sys
import threading
import time
import random

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

class BarberiaMonitor:
  """Implementación del problema del Barbero Dormilón utilizando el concepto

  de MONITOR mediante variables de condición de Python (threading.Condition).
  """

  def __init__(self, num_sillas_espera=3):
    self.num_sillas = num_sillas_espera
    self.clientes_esperando = 0

    # Cerrojo implícito del Monitor y variables de condición asociadas
    self.lock = threading.Lock()
    self.cond_barbero = threading.Condition(self.lock)
    self.cond_sala_espera = threading.Condition(self.lock)
    self.cond_corte = threading.Condition(self.lock)

    # Variables de estado protegidas por el monitor
    self.silla_barbero_ocupada = False
    self.cliente_listo_en_sillon = False
    self.corte_terminado = False
    self.barberia_abierta = True

  def entrar_cliente(self, cliente_id):
    """Invocado por el hilo Cliente al llegar a la barbería.

    Retorna True si fue atendido, False si la sala estaba llena y se marchó.
    """
    with self.lock:
      print(
          f"👤 Cliente {cliente_id} llega a la barbería. (Sillas ocupadas:"
          f" {self.clientes_esperando}/{self.num_sillas})"
      )

      # 1. Capacidad agotada: el cliente se retira inmediatamente
      if self.clientes_esperando >= self.num_sillas:
        print(
            f"🚪 [SALA LLENA] Cliente {cliente_id} se va sin cortarse el pelo."
        )
        return False

      # 2. Hay espacio: toma asiento en una silla de la sala de espera
      self.clientes_esperando += 1
      print(
          f"🪑 Cliente {cliente_id} toma asiento en la sala de espera. (En"
          f" espera: {self.clientes_esperando})"
      )

      # 3. Notificar al barbero por si se encuentra durmiendo
      self.cond_barbero.notify()

      # 4. Esperar su turno: si el sillón está ocupado, espera pasivamente en la sala
      while self.silla_barbero_ocupada:
        self.cond_sala_espera.wait()

      # 5. El cliente es convocado, libera su silla de espera y pasa al sillón
      self.clientes_esperando -= 1
      self.silla_barbero_ocupada = True
      self.cliente_listo_en_sillon = True
      self.corte_terminado = False
      print(
          f"✂️ Cliente {cliente_id} se sienta en el sillón del barbero para el"
          " corte."
      )

      # Notificar al barbero que el cliente ya está acomodado en el sillón
      self.cond_barbero.notify()

      # 6. Esperar a que el barbero termine el corte de cabello
      while not self.corte_terminado:
        self.cond_corte.wait()

      # 7. Corte concluido: el cliente desocupa el sillón y se marcha
      self.corte_terminado = False
      self.silla_barbero_ocupada = False
      self.cliente_listo_en_sillon = False
      print(
          f"💈 Cliente {cliente_id} terminó su corte y sale feliz de la"
          " barbería."
      )

      # Notificar ÚNICAMENTE al barbero que el sillón físico ha quedado libre
      self.cond_barbero.notify()
      return True

  def atender_siguiente_cliente(self):
    """Invocado cíclicamente por el hilo Barbero para recibir trabajo."""
    with self.lock:
      # Mientras no haya nadie en el sillón de atención y la barbería continúe abierta
      while not self.cliente_listo_en_sillon and self.barberia_abierta:
        if self.clientes_esperando == 0:
          print("😴 El barbero no ve clientes y se duerme en su sillón...")
          self.cond_barbero.wait()
        else:
          # Hay clientes en sala: el barbero llama al siguiente comensal
          print("🔔 El barbero llama al siguiente cliente de la sala de espera.")
          self.cond_sala_espera.notify()
          # Espera pasiva hasta que el cliente llamado se acomode en el sillón
          self.cond_barbero.wait()

      # Condición de cierre de jornada laboral
      if (
          not self.barberia_abierta
          and not self.cliente_listo_en_sillon
          and self.clientes_esperando == 0
      ):
        print(
            "🏁 La barbería cerró. El barbero recoge sus herramientas y se va"
            " a casa."
        )
        return False

      return True

  # Alias pedagógico
  esperar_cliente_para_corte = atender_siguiente_cliente

  def finalizar_corte(self):
    """El barbero da por terminado el corte y sincroniza la salida del cliente."""
    with self.lock:
      self.corte_terminado = True
      # Despertar al cliente que está esperando en el sillón
      self.cond_corte.notify()

      # Esperar a que el cliente se baje del sillón y libere el recurso físico
      while self.silla_barbero_ocupada:
        self.cond_barbero.wait()

  def cerrar_barberia(self):
    """Cierra la barbería y despierta a todas las hebras en espera para finalización limpia."""
    with self.lock:
      self.barberia_abierta = False
      self.cond_barbero.notify_all()
      self.cond_sala_espera.notify_all()
      self.cond_corte.notify_all()


def hilo_barbero(barberia):
  """Ciclo de vida del proceso servidor (Barbero)."""
  while True:
    hay_cliente = barberia.atender_siguiente_cliente()
    if not hay_cliente:
      break
    print("✂️ [Barbero] Cortando el cabello...")
    time.sleep(random.uniform(0.1, 0.2))
    barberia.finalizar_corte()


def hilo_cliente(barberia, cliente_id):
  """Ciclo de vida del proceso cliente."""
  time.sleep(random.uniform(0.02, 0.25))
  barberia.entrar_cliente(cliente_id)


if __name__ == "__main__":
  print("=" * 60)
  print(" Barbería con Monitores y Variables de Condición (UNJu FI)")
  print("=" * 60)

  barberia = BarberiaMonitor(num_sillas_espera=3)

  t_barbero = threading.Thread(
      target=hilo_barbero, args=(barberia,), name="Barbero"
  )
  t_barbero.start()

  # Llegan 8 clientes de manera concurrente
  clientes = []
  for i in range(1, 9):
    t_cli = threading.Thread(
        target=hilo_cliente, args=(barberia, i), name=f"Cliente-{i}"
    )
    clientes.append(t_cli)
    t_cli.start()

  # Esperar a que todos los clientes completen su intento de entrada
  for t_cli in clientes:
    t_cli.join()

  time.sleep(0.3)
  barberia.cerrar_barberia()
  t_barbero.join()

  print("=" * 60)
  print(
      " Simulación de Barbería finalizada correctamente sin Deadlock ni"
      " inconsistencias."
  )
  print("=" * 60)