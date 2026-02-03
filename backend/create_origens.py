"""
Script para criar origens padrão no banco de dados
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from crm.models import Origem

origens = [
    "Busca Paga | Google",
    "Busca Paga | Facebook",
    "Busca Paga | Instagram",
    "Busca Organica | Google",
    "Busca Orgânica | Yahoo",
    "Busca Orgânica | Bing",
    "Facebook",
    "Instagram",
    "LinkedIn",
    "YouTube",
    "WhatsApp",
    "Tráfego Direto Site",
    "Prospecção",
    "Mentoria",
    "MBA Fashion Day",
    "Agreste Tex",
    "Comtex",
    "Febratex",
    "Maquintex",
    "Indicação Parceiros",
    "Indicação Cliente",
    "Indicação Equipe",
]

created = 0
for nome in origens:
    obj, was_created = Origem.objects.get_or_create(nome=nome, defaults={'ativo': True})
    if was_created:
        created += 1
        print(f"  ✅ Criada: {nome}")
    else:
        print(f"  ⏭️  Já existe: {nome}")

print(f"\n📊 Total: {len(origens)} | Criadas: {created} | Já existiam: {len(origens) - created}")
