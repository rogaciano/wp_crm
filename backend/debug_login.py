import os
import django
import json
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from crm.models import User

def test_login(username, password):
    url = "http://localhost:8000/api/auth/login/"
    print(f"Testando login para '{username}' com senha '{password}'...")
    try:
        response = requests.post(url, json={"username": username, "password": password}, timeout=5)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✓ SUCESSO!")
            return True
        else:
            print(f"✗ FALHA: {response.json()}")
            return False
    except Exception as e:
        print(f"✗ ERRO: {e}")
        return False

# Verificar se rogaciano tem senha definida (pelo menos se o hash não está vazio)
u = User.objects.get(username='rogaciano')
print(f"User: {u.username}, Has Password: {u.has_usable_password()}")

# Tenta senhas comuns
senhas = ['admin123', 'password123', 'rogaciano123', 'crm123', 'senha123']
found = False
for s in senhas:
    if test_login('rogaciano', s):
        found = True
        break

if not found:
    print("\nNenhuma das senhas comuns funcionou.")
