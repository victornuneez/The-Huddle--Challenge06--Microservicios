
"""
Microservicio de Autenticacion.
Tiene ENDPOINTS para registrar al usuario, iniciar sesion y validar sesion.
Tiene funciones auxiliares para generar y validar tokens.
"""


from flask import Flask, request, jsonify

# Importamos del submodulo '.security' dos funciones que sirven para trabajar con contrasenhas de forma segura
from werkzeug.security import generate_password_hash, check_password_hash

# Importamos del modulo datetime las clases 'datetime' y 'timedelta' para manejar fechas y tiempos, para saber cuando se crea el token y cuando vence.
from datetime import datetime, timedelta, timezone

# Este modulo sirve para cargar variables de entorno desde un archivo .env al sistema o programa.
from dotenv import load_dotenv

# Libreria que nos permite interacturar con el sistema operativo desde python.
import os

import database

# Importamos la libreria que sirve para crear y validar tokens.
import jwt 


# ==========================================================
# SE LLAMA CLAVE SECRETA Y SE DEFINE LA EXPIRACION DEL TOKEN
# ==========================================================

# Esta funcion lee el archivo ".env", carga las variables en el entorno del sistema.
load_dotenv()

# Accedemos a la variable del archivo .env y la guardamos para usarla.
CLAVE_SECRETA = os.getenv("JWT_CLAVE_SECRETA")

if not CLAVE_SECRETA:
    raise RuntimeError("JWT_CLAVE_SECRETA no definida") # (raise lanza error y detiene el programa, 'RuntimeError' error generico para problemas de ejecucion)

# Definimos el tiempo de expiracion del token.
EXPIRACION = timedelta(hours=1)


# =========================
# Creamos el servidor Flask
# =========================
app = Flask(__name__)


# ====================
# FUNCIONES AUXILIARES
# ====================

# Funcion que genera un token valido al usuario para acceder al servidor.
def generar_token(user_id, username):
    
    # Obtenemos el momento de expiracion del token generado.
    fecha_expiracion = datetime.now(timezone.utc) + EXPIRACION
    
    # Contenido del token, quien es el usuario y hasta cuando es valido el token.
    payload = {
        "user_id": user_id,
        "usuario": username, 
        "expiracion": int(fecha_expiracion.timestamp()) # suma la hora actual + el tiempo que dura el token y guarda el momento de expiracion del token.
    }

    # Crea un JWT firmado con "HS256" usando la clave secreta para que nadie pueda modificar el token sin la clave secreta.(No oculta datos)
    token = jwt.encode(payload, CLAVE_SECRETA, algorithm="HS256")
    return token


# Funcion que valida el token del usuario. Devuelve un diccionario indicando si es valido el token y el nombre de usuario.
def validar_token(token):
    try:
        payload = jwt.decode(token, CLAVE_SECRETA, algorithms=["HS256"]) # Decodifica el token recibido usando la clave secreta y el algortimo HS256.
        user_id = payload.get("user_id")
        username = payload.get("usuario")
        fecha_expiracion = payload.get("expiracion")

        # Convertimos a un formato facil de leer la fecha y hora de expiracion del codigo.
        exp_legible = datetime.fromtimestamp(fecha_expiracion, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        return {"valid": True, "username": username,"user_id": user_id, "expiracion": exp_legible}
    
    # Captura el error cuando el token expire. 
    except jwt.ExpiredSignatureError:
        return {"valid": False, "Error": "Token Expirado"}
    
    # Captura el error de tokens invalidos.
    except jwt.InvalidTokenError:
        return {"valid": False, "Error": "Token invalido"}


# ======================
# ENDPOINTS DEL SERVIDOR
# ======================

# Funcion que registra el usuario en la base de datos.
@app.route('/register', methods=['POST'])
def registrar_usuario():
        # Convertimos la peticion que recibimos a un diccionario con los datos y los obtenemos.
        datos = request.get_json()
        username = datos.get('username')
        password = datos.get('password')

        # Verificamos si el usuario ya existe
        if database.buscar_usuario(username):
            return jsonify({"error": "El usuario ya existe" }), 400
        
        # Hasheamos la contrasenha(convierte la contrasenha en un codigo irreconocible) 
        password_hash = generate_password_hash(password)

        # Guardamos en la base de datos el nombre de usuario y su contrasenha hasheada.
        database.guardar_usuario(username, password_hash)
        return jsonify({"message": "Usuario registrado correctamente en la base de datos"}), 201


# Funcion que valida el login del usuario y le devuelve un JTW temporal para accerder al Servicio del programa.
@app.route('/login', methods=['POST'])
def iniciar_sesion():
    
        # Convertimos la peticion recibida a un diccionario y obtenemos los datos del usuario que quiere iniciar sesion.
        datos = request.get_json()
        username = datos.get('username')
        password = datos.get('password')

        if not username or not password:
            return({"Error!": "Username y password requeridos"}), 404
        
        # Buscamos el nombre de usuario en la base de datos del servidor.(Devuelve la fila entera del usuario en una tupla)
        user = database.buscar_usuario(username)
        if not user:
            return jsonify({"Error": "Usuario no encontrado"}), 404
        
        # Accedemos al contenido de password_hash en la base de datos.(Tercera columna)
        password_hash = user[2] 
        if not check_password_hash(password_hash, password): # Comparamos las contrasenhas hasheadas.
            return jsonify({"Error": "Contrasenha Incorrecta"}), 401

        # Generamos el token temporal y le enviamos al usuario.(user_id, username)
        token = generar_token(user[0], username)
        return jsonify({"token": token}), 200
    


# Funcion que valida el token del usuario.
@app.route('/validate', methods=['POST'])
def validar_sesion():

        # Convierte el json que envio el usuario a un diccionario y guarda el token.   
        datos = request.get_json("token") 
        token = datos.get("token") 

        if not token:
            return jsonify({"Error": "Token requerido"}), 400
        
        # Validamos el token recibido del usuario y lo guardamos.
        resultado = validar_token(token)

        # Se verifica si el token del usuario es valido o no para devolver una respuesta al cliente.
        if resultado["valid"]:
            return jsonify({"valid": True, 
                            "user_id": resultado["user_id"], 
                            "username": resultado["username"], 
                            "token expira en(Horario Global)": resultado["expiracion"]}), 200
        
        else:
            return jsonify({"valid": False, "Error": resultado.get("Error")}), 401 # Devolvemos el mensaje de error que pudo generar la funcion de validar token.

# Ejecutamos la app
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True) 
