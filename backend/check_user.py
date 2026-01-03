import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from crm.models import User

try:
    u = User.objects.get(username='rogaciano')
    print(f"User: {u.username}")
    print(f"Perfil: {u.perfil}")
    print(f"Canal: {u.canal.nome if u.canal else 'N/A'}")
except User.DoesNotExist:
    print("Usuário 'rogaciano' não encontrado.")
except Exception as e:
    print(f"Erro: {e}")
