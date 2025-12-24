
from flask import Flask, request, jsonify

# Importamos el modulo requests para poder hacer peticiones a los demas microservicios
import requests

import database

# ==============
# SERVIDOR FLASK
# ==============

app = Flask(__name__)

# Inicializamos la base de datos.
database.iniciar_bd()

# Definimos la URL con el ENDPOINT donde queremos hacer una peticion.
URL_SERVICIO_AUT = "http://127.0.0.1:5000/validate"

# ================
# FUNCION AUXILIAR
# ================

# Funcion que valida el token del usuario.
def validar_token(token):
    try:
        headers = {"Content-Type": "application/json"}
        datos = {"token": token}

        # Hacemos una peticion al microservicio de autenticacion para validar el token que recibimos
        respuesta = requests.post(URL_SERVICIO_AUT, json=datos, headers=headers) 

        if respuesta.status_code != 200:
            return None # Devolvemos none(token invalido o expirado)
        
        return respuesta.json()
    
    except Exception as error:
        print(f"Error al validar token: {error}")

# ======================
# ENDPOINTS DEL SERVIDOR
# ======================

# Funcion para recibir y crear tareas.
@app.route("/tasks", methods=['POST'])
def crear_tarea():
    try:
        # Obtenemos de la peticion el header de autorizacion y lo guardamos.
        header_autorizacion = request.headers.get("Authorization")

        if not header_autorizacion:
            return jsonify({"error": "Token requerido"}), 401
        
        # Reemplazamos la palabra bearer del token que recibimos dejando solo el token limpio listo para usarse.
        token = header_autorizacion.replace("Bearer ", "")
        resultado = validar_token(token)
        print("Resultado de validar_token:", resultado)

        if not resultado.get("valid"):
            return jsonify({"Error": "Token invalido"}), 401
        
        # Obtenemos el id_user
        user_id = resultado.get("user_id")
        print("user_id desde token:", user_id)

        datos = request.get_json()
        tarea = datos.get("tarea") # Obtenemos la tarea que envio el usuario.

        if not tarea:
            return jsonify({"Error": "Tarea requerido"}), 400
        
        # Agregamos a la base de datos el user_id y la tarea.
        database.agregar_tarea(user_id, tarea)

        return jsonify({"message": "Tarea creada correctamente"})
    
    except Exception as error:
        print(f"Error, no se pudo guardar la tarea: {error}")
        return jsonify({"error": str(error)}), 500


# Funcion para recibir filtros y enviar las tareas solicitadas.
@app.route("/task", methods=["GET"])
def listar_tareas():

    # Obtenemos el token del header que envio el usuario y lo guardamos.
    header_autorizacion = request.headers.get("Authorization")

    if not header_autorizacion:
        return jsonify({"Error": "Token requerido"}), 401
    
    # limpiamos el token, para poder validar solo el valor del token.
    token = header_autorizacion.replace("Bearer ", "")
    resultado = validar_token(token)

    if not resultado.get("valid"):
        return jsonify({"Error": "Token invalido"}), 401
    
    # Obtenemos el user_id y filtramos todas las tareas del usuario por su user_id.
    user_id = resultado.get("user_id")
    tareas = database.obtener_tareas(user_id)

    return jsonify({"user_id": user_id, "tareas": tareas}), 200


# Funcion para actualizar una tarea como completada.
@app.route("/tasks/<int:task_id>/complete", methods=["PUT"]) # "<int:task_id>" variable dinamica, tendra el valor que le asigne el usuario en su peticion.
def completar_tarea(task_id):

    # Obtenemos el token del header que envio el usuario.
    header_autorizacion = request.headers.get("Authorization")

    if not header_autorizacion:
        return jsonify({"Error": "Token Requerido"}), 401
    
    # Obtenemos solo el valor del token.
    token = header_autorizacion.replace("Bearer ","")
    resultado = validar_token(token)

    if not resultado.get("valid"):
        return jsonify({"Error": "Token invalido"}), 401
    
    # Obtenemos el "user_id" de quien se va a actualizar su tarea
    user_id = resultado.get("user_id")

    # Usamos la funcion de marcar la tarea como completada de la base de datos.
    exito = database.marcar_completada(user_id, task_id)

    if not exito:
        return jsonify({"Error": "Tarea no encontrada o no pertenece al usuario"}), 404
    
    return jsonify({"message": "Tarea marcada como completada"}), 200


# Funcion para eliminar tareas. (<int:task_id>) variable dinamica donde el usuario pondra el numero de fila exacto de la tarea que quiere borrar.
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def eliminar_tarea(task_id):

    # Obtenemos el token del header que envio el usuario.
    header_autorizacion = request.headers.get("Authorization")

    if not header_autorizacion:
        return jsonify({"Error": "Token requerido"}), 401
    
    # Limpiamos el token.
    token = header_autorizacion.replace("Bearer ", "")
    resultado = validar_token(token) 

    if not resultado.get("valid"):
        return jsonify({"Error": "Token Requerido"}), 401 
    
    user_id = resultado.get("user_id")
    exito = database.eliminar_tarea(user_id, task_id)

    # Verificamos si se pudo eliminar la tarea.
    if not exito:
        return jsonify({"Error": "Tarea no encontrada o no pertenece al usuario"}), 404
    
    return jsonify({"message": "Tarea eliminada correctamente"}), 200

    
if __name__ == "__main__":

    print("\n" + "="*60)
    print("Microservicio de Tareas")
    print("="*60)
    print("IP: 127.0.0.1")
    print("Puerto: 5001")
    print("\nENDPOINTS DISPONIBLES:")
    print("POST  /tasks  -> Crea y agrega tareas")
    print("GET /tasks -> Recibe filtros y devuelve las tareas solicitadas")
    print("PUT /tasks/<int:task_id>/complete -> Actualiza una tarea como completada")
    print("DELETE /tasks/<int:task_id> -> Elimina tareas\n")

    app.run(host="127.0.0.1", port=5001, debug=True)
