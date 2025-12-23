import requests

AUTH_URL = "http://127.0.0.1:5000"
TASK_URL = "http://127.0.0.1:5001"
NOTIF_URL = "http://127.0.0.1:5002"

usuario = {
    "username": "victor",
    "password": "1234"
}

# Login
login = requests.post(f"{AUTH_URL}/login", json=usuario)
token = login.json().get("token")
headers = {"Authorization": f"Bearer {token}"}

print("\n=== NOTIF | GENERAR RECORDATORIO ===")
r = requests.post(f"{NOTIF_URL}/recordatorios", headers=headers)
print(r.status_code, r.json())

print("\n=== NOTIF | LISTAR TAREAS PENDIENTES ===")
r = requests.get(f"{NOTIF_URL}/tasks/pendientes", headers=headers)
print(r.status_code, r.json())
