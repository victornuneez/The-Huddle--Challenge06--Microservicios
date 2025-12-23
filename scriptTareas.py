import requests

AUTH_URL = "http://127.0.0.1:5000"
TASK_URL = "http://127.0.0.1:5001"

usuario = {
    "username": "victor",
    "password": "1234"
}

# Login para obtener token
login = requests.post(f"{AUTH_URL}/login", json=usuario)
token = login.json().get("token")

headers = {"Authorization": f"Bearer {token}"}

print("\n=== TASK | CREAR TAREA ===")
r = requests.post(f"{TASK_URL}/tasks", json={"tarea": "Aprender microservicios"}, headers=headers)
print(r.status_code, r.json())

print("\n=== TASK | LISTAR TAREAS ===")
r = requests.get(f"{TASK_URL}/task", headers=headers)
print(r.status_code, r.json())

tareas = r.json().get("tareas", [])

if tareas:
    task_id = tareas[0]["id"]

    print("\n=== TASK | COMPLETAR TAREA ===")
    r = requests.put(f"{TASK_URL}/tasks/{task_id}/complete", headers=headers)
    print(r.status_code, r.json())

    print("\n=== TASK | ELIMINAR TAREA ===")
    r = requests.delete(f"{TASK_URL}/tasks/{task_id}", headers=headers)
    print(r.status_code, r.json())
