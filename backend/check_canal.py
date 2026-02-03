import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from crm.models import Canal, Oportunidade

# Verifica canais
print("=== CANAIS ===")
for c in Canal.objects.all():
    print(f"  {c.nome} | slug: {c.slug} | responsavel: {c.responsavel}")

# Verifica última oportunidade
print("\n=== ÚLTIMA OPORTUNIDADE ===")
opp = Oportunidade.objects.last()
if opp:
    print(f"  ID: {opp.id}")
    print(f"  Nome: {opp.nome}")
    print(f"  Proprietário: {opp.proprietario}")
    print(f"  Conta: {opp.conta}")
    if opp.conta:
        print(f"  Conta.canal: {opp.conta.canal}")
