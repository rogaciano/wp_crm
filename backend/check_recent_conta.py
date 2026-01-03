import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from crm.models import Conta

try:
    c = Conta.objects.get(id=10)
    print(f"Nome: {c.nome_empresa}")
    print(f"Canal: {c.canal.nome if c.canal else 'N/A'}")
    print(f"Proprietário: {c.proprietario.username}")
    print(f"Data Criação: {c.data_criacao}")
except Conta.DoesNotExist:
    print("Conta com ID 10 não encontrada.")
except Exception as e:
    print(f"Erro: {e}")
