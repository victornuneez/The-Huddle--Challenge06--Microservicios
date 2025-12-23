import requests

BASE_URL = "http://127.0.0.1:5000"

usuario = {
    "username": "victor",
    "password": "1234"
}

print("\n=== AUTH | REGISTER ===")
r = requests.post(f"{BASE_URL}/register", json=usuario)
print(r.status_code, r.json())

print("\n=== AUTH | LOGIN ===")
r = requests.post(f"{BASE_URL}/login", json=usuario)
print(r.status_code, r.json())

token = r.json().get("token")

print("\n=== AUTH | VALIDATE TOKEN ===")
r = requests.post(f"{BASE_URL}/validate", json={"token": token})
print(r.status_code, r.json())
