"""
Circuit Breaker.

Monitorea las llamadas a servicios externos.
Si detecta muchos fallos, "abre el circuito" y rechaza peticiones temporalmente,
permitiendo que el servicio fallido se recupere sin colapsar todo el sistema

"""
# La clase del modulo enum nos permite crear valores fijos, un conjunto fijo de estados posibles del circui breaker.
from enum import Enum
import time

"""
Estados posibles del Circuit Breaker:
- CLOSED: Funcionamiento normal, todas las peticiones pasan
- OPEN: Circuito abierto, rechaza peticiones sin intentarlas
- HALF_OPEN: Prueba si el servicio se recupero.
"""

# Definimos los estados del circuit broker
class EstadoCircuito(Enum):

    CLOSED = "CLOSED"       # Circuit Breaker cerrado, todo funciona normal las peticiones se ejecutan como siempre.
    OPEN = "OPEN"           # Circuit Breaker abierto, bloquea hacer nuevas solicitudes a el microservicio que esta fallando.
    HALF_OPEN = "HALF_OPEN" # Circuit Breaker semi abierto, prueba hacer algunas solicitudes al microservicio que estaba fallando.(fallando = OPEN, funcionando = CLOSED)


class CircuitBreaker:

    def __init__(self, max_fallos=3, tiempo_espera=20, nombre="Servicio"):

        self.max_fallos = max_fallos        # Cantidad de fallos consecutivos antes de abrir el circuito
        self.tiempo_espera = tiempo_espera  # Tiempo que espera antes de pasar de OPEN a HALF-OPEN
        self.nombre = nombre                # Nombre ser servicio que protege circuit breaker.

        # Estado inicial del Circuit Breaker
        self.num_fallos = 0  # Cuenta el numero de fallos hasta llegar al maximo, entonces el circuit breaker cambia a OPEN.
        self.estado = EstadoCircuito.CLOSED # Indica en qué estado está el breaker ahora
        self.momento_apertura = None # Guarda el momento en que el breaker paso a OPEN, para poder medir cuánto tiempo ha estado abierto y saber cuándo pasar a HALF-OPEN.

    """
    Es el filtro principal antes de hacer cualquier petición a un microservicio.
    """
    # Esta funcion permite verificar si se puede hacer una peticion.(True si se permite, False si está bloqueado)
    def permitir_peticion(self):

        # Verificamos si circuit breaker esta abierto.
        if  self.estado == EstadoCircuito.OPEN:
            tiempo_pasado = time.time() - self.momento_apertura #  Calculamos cuanto tiempo paso desde que se abrio(OPEN)

            # Verificamos si se cumplio el timepo de espera para probar si ya funciona el microservicio que queremos usar.
            if tiempo_pasado >= self.tiempo_espera:
                self.estado = EstadoCircuito.HALF_OPEN # Dejamos pasar una peticion de prueba en el estado "HALF_OPEN"

                print(f"[{self.nombre}] Estado: HALF_OPEN - Probando recuperacion")
                return True
            
            else:
                # Todavia no paso el tiempo de espera.(sigue bloqueado)
                return False
        
        # Si esta CLOSED O HALF_OPEN, dejamos pasar la peticion.
        return True
    
    
    # Esta funcion registra una peticion exitosa, resetea num_fallos y cierra el circuito si estaba en HALF_OPEN.
    def registrar_exito(self):

        # Reiniciamos el contador de fallos consecutivos.(Lo reinicia una peticion exitosa)
        self.num_fallos = 0

        # Verificamos si el circuit breaker estaba en HALF_OPEN, significa que el servicio se recupero la prueba salio bien.
        if self.estado == EstadoCircuito.HALF_OPEN:
            self.estado = EstadoCircuito.CLOSED
            print(f"[{self.nombre}] Estado: CLOSED - Servicio externo recuperado")

        # Si estaba cerrado, simplemente seguimos contando éxitos.(registro visual, ayuda a saber que las cosas van bien)
        else:
            print(f"[{self.nombre}] Peticion exitosa")


    # Esta funcion registra una peticion fallida.
    def registrar_fallo(self, error= None):

        # Aumentamos el contador de fallos consecutivos.
        self.num_fallos += 1

        # Si se alcanza el limite, abrimos el circuito
        if self.num_fallos >= self.max_fallos:
            self.estado = EstadoCircuito.OPEN  
            self.momento_apertura = time.time() # Registra el momento en que volvió a OPEN.

            print(f"[{self.nombre}] Estado: OPEN - Circuito abierto")

        # Si estábamos en HALF_OPEN y falla la prueba, volvemos a OPEN
        if self.estado == EstadoCircuito.HALF_OPEN:
            self.estado = EstadoCircuito.OPEN
            self.momento_apertura = time.time() # Registra el momento en que volvió a OPEN, para saber cuánto tiempo esperar antes de probar otra vez
            print(f"[{self.nombre}] Estado: OPEN - Servicio externo aún no recuperado")


    # Ejecuta una funcion protegida por Circuit Breaker. Devuelve el resultado de la función si tiene éxito, None si falla o si el circuito está bloqueado
    def ejecutar(self, funcion):

        # Verificamos si podemos hacer una peticion.
        if not self.permitir_peticion():
            return None # bloqueado porque el circuito esta en estado OPEN.
        
        try:
            # Ejecuta la función que le pasaste como argumento a tu Circuit Breaker. Guarda el valor que devuelva esa función en la variable resultado. 
            resultado = funcion()  # Si la función falla (lanza un error), no se guarda nada y el flujo pasa al except.
            self.registrar_exito()
            return resultado # Devolvemos el resultado de la función para que el microservicio que hizo la llamada pueda seguir trabajando con los datos normalmente.
        
        # except, si hubo fallo, se registra fallo y controla el estado del breaker.
        except Exception as error:
            self.registrar_fallo(error)
            return None # Devuelve None para que tu servicio sepa que la llamada falló, sin romper todo el flujo