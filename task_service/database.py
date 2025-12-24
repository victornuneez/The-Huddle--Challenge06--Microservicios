
"""
Creamos la base de datos sqlite del microservicio de tareas.
Tiene funciones de crear tabla, agregar tareas, obtener tareas, marcar tareas como completadas y la funcion de eliminar tareas.
"""

import sqlite3
from datetime import datetime

DB = "tasks.db"

# Funcion que crea la base de datos.
def iniciar_bd():
    with sqlite3.connect(DB, timeout=5) as conexion:
        cursor = conexion.cursor()
    
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            tarea TEXT NOT NULL,
            fecha_creacion TEXT NOT NULL,
            fecha_vencimiento TEXT,
            completada INTEGER DEFAULT 0
        ) 
        """)

        conexion.commit()
    


# Funcion para agregar tarea en la base de datos.
def agregar_tarea(user_id, tarea, fecha_vencimiento=None):
    with sqlite3.connect(DB, timeout=5) as conexion:
        cursor = conexion.cursor()
        fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
        INSERT INTO Tareas (user_id, tarea, fecha_creacion, fecha_vencimiento) VALUES (?,?,?,?)
    """, (user_id, tarea, fecha_creacion, fecha_vencimiento))
        
        conexion.commit()
    


# Funcion que obtiene una lista de todas las tareas de un usuario.
def obtener_tareas(user_id):
    with sqlite3.connect(DB) as conexion:
        conexion.row_factory = sqlite3.Row # Permite que cada fila que obtengamos se pueda acceder por el nombre de la columna, no solo por el indice.
        cursor = conexion.cursor()

        # Consultamos todas las tareas que tenga el usuario(user_id).
        cursor.execute("""
        SELECT id, tarea, completada, fecha_creacion FROM Tareas WHERE user_id = ?
    """, (user_id,))
        
        # Obtenemos todas las filas que cumplen la condicion de la consulta.(lista de tuplas)(Cada tupla = fila tabla, Cada fila tabla = tipo de objeto sqlite3.Row).
        filas = cursor.fetchall()
    
        # Se recorre cada fila de la lista de tuplas(sqlite3.Row) y la convertimos a un diccionario.(Creamos una nueva lista pero de diccionarios)
        tareas = [dict(fila) for fila in filas] 
        
        # Convertimos el valor de las columnas 'completadas' en un booleano.(Para no tener que adividar que significa 0 o 1).
        for tarea in tareas:
            tarea["completada"] = bool(tarea["completada"])

        return tareas


# Esta funcion marca una tarea por vez como completada.
def marcar_completada(user_id, task_id):
    with sqlite3.connect(DB, timeout=5) as conexion:
        cursor = conexion.cursor()

        cursor.execute("""
        UPDATE Tareas SET completada = 1 WHERE id = ? AND user_id = ?
        """, (task_id, user_id))

        conexion.commit()
        cambios = cursor.rowcount # obtiene el numero de filas modificadas.

        # True si actualizo alguna fila, False si no.
        return cambios > 0 


# Funcion para elimina una tarea por vez.
def eliminar_tarea(user_id, task_id):

    with sqlite3.connect(DB, timeout=5) as conexion:
        cursor = conexion.cursor()

        cursor.execute("""
            DELETE FROM Tareas WHERE id = ? AND user_id = ?
        """, (task_id, user_id))

        conexion.commit()
        cambios = cursor.rowcount # obtiene el numero de filas modificadas
    
        return cambios > 0 # True si actualiza alguna fila. False si no.