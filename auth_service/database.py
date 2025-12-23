
"""
Creamos la base de datos con la tabla usuarios.
Tiene funciones para crear la base de datos, guardar usuarios en la tabla y consultar usuarios de la base de datos.
"""

import sqlite3
from datetime import datetime

DB = "auth_service.db"

# Funcion que crea la base de datos y la tabla Usuarios.
def iniciar_db():

    conexion = sqlite3.connect(DB)
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Usuarios (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        fecha_creacion TEXT NOT NULL
        )
    """)
    
    conexion.commit()
    conexion.close()

# Funcion que guarda el nombre de usuario, la contrasenha hasheada y la fecha en el momento en que se guarda el usuario en la base de datos.
def guardar_usuario(username, password_hash):

    conexion = sqlite3.connect(DB)
    cursor = conexion.cursor()
    fecha_creacion = datetime.utcnow().isoformat()
    
    cursor.execute("""INSERT INTO Usuarios 
                (username, password_hash, fecha_creacion) 
                VALUES (?,?,?)""",
                (username, password_hash, fecha_creacion))

    conexion.commit()
    conexion.close()

# Funcion que devuelve el nombre de un usuario.
def buscar_usuario(username):

    conexion = sqlite3.connect(DB)
    cursor = conexion.cursor()
    
    # Esta consulta devuelve todos los username que se llamen como el username ingresado en la consulta.
    cursor.execute("SELECT * FROM Usuarios WHERE username = ?", (username,))
    user = cursor.fetchone() # Devolvemos solo un resultado.(El primero)

    conexion.close()
    return user 

# Inicializamos la base de datos al arrancar el microservicio.
iniciar_db()
print("Base de datos Inicializada Correctamente")
print