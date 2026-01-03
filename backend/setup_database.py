"""
Script para criar dados iniciais do sistema CRM
Execute: python manage.py shell < setup_database.py
"""

from django.contrib.auth import get_user_model
from crm.models import Canal, EstagioFunil

User = get_user_model()

print("=== Criando dados iniciais do CRM ===\n")

# Criar canais
print("Criando Canais...")
canais_data = [
    {"nome": "Pernambuco"},
    {"nome": "Paraíba"},
    {"nome": "Fortaleza"},
    {"nome": "São Paulo"},
    {"nome": "Brasilia"},
]

for canal_data in canais_data:
    canal, created = Canal.objects.get_or_create(**canal_data)
    if created:
        print(f"  ✓ Canal criado: {canal.nome}")
    else:
        print(f"  - Canal já existe: {canal.nome}")

# Criar estágios do funil
print("\nCriando Estágios do Funil...")
estagios_data = [
    {"nome": "Prospecção", "ordem": 1, "tipo": "ABERTO", "cor": "#3B82F6"},
    {"nome": "Qualificação", "ordem": 2, "tipo": "ABERTO", "cor": "#8B5CF6"},
    {"nome": "Proposta", "ordem": 3, "tipo": "ABERTO", "cor": "#EC4899"},
    {"nome": "Negociação", "ordem": 4, "tipo": "ABERTO", "cor": "#F59E0B"},
    {"nome": "Fechado - Ganho", "ordem": 5, "tipo": "GANHO", "cor": "#10B981"},
    {"nome": "Fechado - Perdido", "ordem": 6, "tipo": "PERDIDO", "cor": "#EF4444"},
]

for estagio_data in estagios_data:
    estagio, created = EstagioFunil.objects.get_or_create(
        nome=estagio_data["nome"],
        defaults=estagio_data
    )
    if created:
        print(f"  ✓ Estágio criado: {estagio.nome}")
    else:
        print(f"  - Estágio já existe: {estagio.nome}")

# Criar usuários de exemplo (opcional)
print("\nCriando Usuários de Exemplo...")

# Admin
admin, created = User.objects.get_or_create(
    username="admin",
    defaults={
        "email": "admin@crm.com",
        "first_name": "Administrador",
        "last_name": "Sistema",
        "perfil": "ADMIN",
        "is_staff": True,
        "is_superuser": True,
    }
)
if created:
    admin.set_password("admin123")
    admin.save()
    print(f"  ✓ Admin criado: {admin.username} (senha: admin123)")
else:
    print(f"  - Admin já existe: {admin.username}")

# Responsáveis
canal_sul = Canal.objects.get(nome="Canal Sul")
responsavel_sul, created = User.objects.get_or_create(
    username="resp_sul",
    defaults={
        "email": "resp.sul@crm.com",
        "first_name": "Responsável",
        "last_name": "Sul",
        "perfil": "RESPONSAVEL",
        "canal": canal_sul,
    }
)
if created:
    responsavel_sul.set_password("resp123")
    responsavel_sul.save()
    canal_sul.responsavel = responsavel_sul
    canal_sul.save()
    print(f"  ✓ Responsável criado: {responsavel_sul.username} (senha: resp123)")
else:
    print(f"  - Responsável já existe: {responsavel_sul.username}")

# Vendedores
vendedor1, created = User.objects.get_or_create(
    username="vendedor1",
    defaults={
        "email": "vendedor1@crm.com",
        "first_name": "João",
        "last_name": "Silva",
        "perfil": "VENDEDOR",
        "canal": canal_sul,
    }
)
if created:
    vendedor1.set_password("vend123")
    vendedor1.save()
    print(f"  ✓ Vendedor criado: {vendedor1.username} (senha: vend123)")
else:
    print(f"  - Vendedor já existe: {vendedor1.username}")

vendedor2, created = User.objects.get_or_create(
    username="vendedor2",
    defaults={
        "email": "vendedor2@crm.com",
        "first_name": "Maria",
        "last_name": "Santos",
        "perfil": "VENDEDOR",
        "canal": canal_sul,
    }
)
if created:
    vendedor2.set_password("vend123")
    vendedor2.save()
    print(f"  ✓ Vendedor criado: {vendedor2.username} (senha: vend123)")
else:
    print(f"  - Vendedor já existe: {vendedor2.username}")

print("\n=== Setup concluído! ===")
print("\nUsuários criados:")
print("  • admin / admin123 (Administrador)")
print("  • resp_sul / resp123 (Responsável de Canal)")
print("  • vendedor1 / vend123 (Vendedor)")
print("  • vendedor2 / vend123 (Vendedor)")
print("\nAcesse: http://localhost:8000/admin/ ou http://localhost:5173/")
