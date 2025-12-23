
"""
Microservicio de Recordatorios.
Tiene ENDPOINTS para generar recordatorios, y listar tareas pendientes para devolverlas al cliente.
"""

from flask import Flask, request, jsonify
import requests
import database

# Creamos el servidor Flask
app = Flask(__name__)

# Inicializamos nuestra base de datos.
database.crear_tabla()
print("Base de datos inicializada correctamente")
print()

# Definimos la URL del microservicio de Autenticacion y Tareas, que apuntan a los ENDPOINTS de validar sesion del usuario y listar tareas.
URL_SERVICE_AUTH ="http://127.0.0.1:5000/validate"
URL_SERVICE_TASK = "http://127.0.0.1:5001/task"

# ==========
# ENDOPOINTS
# ==========


# Funcion que notifica al usuario cuantas tareas pendientes tiene, guarda a quien envio el recordatorio(id_user) y el mensaje que le envio en la base de datos.
@app.route("/recordatorios", methods=['POST'])
def generar_recordatorio():

    try:
        # --------------------------------------------
        # OBTENEMOS QUIEN NOS SOLICITO EL RECORDATORIO
        # --------------------------------------------

        # Obtenemos el token de autorizacion del header.
        header_autorizacion = request.headers.get("Authorization")

        if not header_autorizacion:
            return jsonify({"Error": "Token Requerido"}), 401
        
        # Limpiamos el token y obtenemos solo el valor del token
        token = header_autorizacion.replace("Bearer ", "")

        # Hacemos una peticion al microservicio de autenticacion, para validar el token recibido.(ENDPOINT/VALIDATE "POST")
        respuesta = requests.post(URL_SERVICE_AUTH, json={"token": token})

        if respuesta.status_code != 200:
            return jsonify({"Error": "Token invalido"}), 401
        
        # Convertimos la respuesta que en un diccionario.
        datos_autenticacion = respuesta.json()
        user_id = datos_autenticacion.get("user_id") # obtenemos el user_id del diccionario

        if not user_id:
            return jsonify({"error": "Usuario no válido"}), 401

        # -----------------------------------
        # OBTENEMOS LAS TAREAS DE ESE USUARIO
        # -----------------------------------

        # Hacemos una peticion al microservicio de tareas, para que nos devuelva las tareas del usuario(user_id).
        tareas_respuesta = requests.get(URL_SERVICE_TASK, headers={"Authorization": f"Bearer {token}"})

        if tareas_respuesta.status_code != 200:
            return jsonify({"Error": "No se pudieron obtener las tareas"}), 500
        
        # Convertimos la respuesta del microservicio de tareas en una lista de diccionarios.
        datos = tareas_respuesta.json()  
        tareas = datos.get("tareas", []) # Tomamos la lista de tareas del diccionario que devolvio el microservicio de tareas.(Si la clave tareas no existe devolvemos una lista vacia)

        # Creamos una nueva lista de tareas pendientes.
        pendientes = [t for t in tareas 
                    if not t["completada"]]

        if not pendientes:
            mensaje = "No tenes tareas pendientes"

        else:
            mensaje = f"Tenes {len(pendientes)} tareas pendientes"

        # Guardamos el id_user de a quien enviamos el mensaje, y el mensaje.
        database.guardar_recordatorio(user_id, mensaje)

        return jsonify({"mensaje": mensaje}), 200

    except Exception as error:
        print(f"Error, no se pudo generar recordatorio: {error}")
        return jsonify({"error": str(error)}), 500 


# Funcion que devuelve al usuario las tareas que tiene pendiente.
@app.route("/tasks/pendientes", methods=["GET"])
def tareas_pendientes():
    
    # Obtener token de autorization del header.
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        return jsonify({"error": "Token requerido"}), 401

    token = auth_header.replace("Bearer ", "")

    # Hacemos una peticion al microservicio de autenticacion para validar el token recibido.(ENDPOINT/VALIDATE "POST")
    respuesta = requests.post(URL_SERVICE_AUTH, json={"token": token})
    if respuesta.status_code != 200:
        return jsonify({"error": "Token inválido"}), 401

    # Convertimos la respuesta del microservicio de autenticacion en un diccionario.
    Datos_autenticacion = respuesta.json()
    user_id = Datos_autenticacion.get("user_id") # Obtenemos el user_id

    # Hacemos una peticion al Microservicio de Tareas para obtener las tareas del usuario.
    tareas_respuesta = requests.get(URL_SERVICE_TASK, headers={"Authorization": f"Bearer {token}"})
    
    if tareas_respuesta.status_code != 200:
        return jsonify({"error": "No se pudieron obtener las tareas"}), 500

    # Convertimos la respuesta JSON a un diccionario, obtenemos solo la lista de tareas.
    tareas = tareas_respuesta.json().get("tareas", [])
    pendientes = [t for t in tareas 
                if not t["completada"]] # Filtramos solo las tareas pendientes para devolver al usuario.

    return jsonify({"tareas_pendientes": pendientes}), 200



if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5002, debug=True)  