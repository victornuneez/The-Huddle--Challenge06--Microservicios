
"""
Base de datos del Microservicio de Recordatorios.
Tiene funciones para crear la base de datos y la tabla, guardar recordatorios, obtener recordatorios
"""


import sqlite3

from datetime import datetime

# Nombre de la base de datos.
DB = "notificacion.db"

# Funcion para crear base de datos y la tabla 'Recordatorios'
def crear_tabla():

    conexion = sqlite3.connect(DB)
    cursor = conexion.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Recordatorios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        mensaje TEXT NOT NULL,
        fecha_evento TEXT NOT NULL)
    """)

    conexion.commit()
    conexion.close()

# Funcion para guardar recordatorios de un usuario.
def guardar_recordatorio(user_id, mensaje):

    conexion = sqlite3.connect(DB)
    cursor = conexion.cursor()

    # Obtenemos el momento en que vamos a guardar el recordatorio en la base de datos.
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO Recordatorios (user_id, mensaje, fecha_evento) VALUES (?,?,?)    
    """, (user_id, mensaje, fecha_actual))

    conexion.commit()
    conexion.close()

# funcion para obtener recordatorios de un usuario.
def obtener_recordatorios(user_id):

    conexion = sqlite3.connect(DB)
    conexion.row_factory = sqlite3.Row # Permite que cada fila que obtengamos se pueda acceder por el nombre de la columna, no solo por el indice.
    cursor = conexion.cursor()

    cursor.execute("""
    SELECT * FROM Recordatorios WHERE user_id = ?
    """, (user_id,))

    # "fetchall()" devuelve todas las filas que cumplen la condición como una lista de objetos. (sqlite3.Row)
    # Cada fila representa un recordatorio del usuario, accesible por nombre de columna gracias a "sqlite3.Row".
    filas = cursor.fetchall()
    conexion.close()

    # Devolvemos una lista de diccionarios. (Cada fila en un diccionario)(Ahora se puede enviar facilmente al usuario como JSON)
    return [dict(fila) for fila in filas]

