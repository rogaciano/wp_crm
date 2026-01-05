"""
Testa se a API está retornando mensagens corretamente
"""
import os
import sys
import django

# Configura Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import pymysql
pymysql.install_as_MySQLdb()

django.setup()

from crm.models import WhatsappMessage
from django.db.models import Q

def test_api_filter(number):
    """Testa o filtro que a API usa"""
    print(f"\n{'='*60}")
    print(f"TESTANDO FILTRO DA API PARA NÚMERO: {number}")
    print('='*60)

    # Limpa o número (mesmo que a API faz)
    clean_number = ''.join(filter(str.isdigit, str(number)))
    print(f"Número limpo: {clean_number}")

    # Aplica o mesmo filtro que o get_queryset usa
    queryset = WhatsappMessage.objects.filter(
        Q(numero_remetente__icontains=clean_number) |
        Q(numero_destinatario__icontains=clean_number)
    ).order_by('timestamp')

    print(f"\nTotal de mensagens encontradas: {queryset.count()}")

    if queryset.exists():
        print(f"\nPrimeiras 5 mensagens:")
        for i, msg in enumerate(queryset[:5], 1):
            print(f"\n{i}. ID: {msg.id} | de_mim: {msg.de_mim}")
            print(f"   Remetente: {msg.numero_remetente}")
            print(f"   Destinatário: {msg.numero_destinatario}")
            print(f"   Texto: {msg.texto[:50]}...")
            print(f"   Timestamp: {msg.timestamp}")

        print(f"\nÚltimas 5 mensagens:")
        for i, msg in enumerate(queryset.order_by('-timestamp')[:5], 1):
            print(f"\n{i}. ID: {msg.id} | de_mim: {msg.de_mim}")
            print(f"   Remetente: {msg.numero_remetente}")
            print(f"   Destinatário: {msg.numero_destinatario}")
            print(f"   Texto: {msg.texto[:50]}...")
            print(f"   Timestamp: {msg.timestamp}")
    else:
        print("\n❌ NENHUMA MENSAGEM ENCONTRADA!")
        print("\nVamos ver todas as mensagens no banco:")
        all_msgs = WhatsappMessage.objects.all()[:5]
        for msg in all_msgs:
            print(f"  - Remetente: {msg.numero_remetente} | Destinatário: {msg.numero_destinatario}")

if __name__ == "__main__":
    # Testa com os números que aparecem nas mensagens
    test_api_filter("5581999216560")  # Rogaciano
    test_api_filter("81999216560")     # Sem DDI
    test_api_filter("+55 81 99921-6560")  # Formatado
