"""
Script de teste manual para verificar a integração WhatsApp
Execute: python backend/test_whatsapp_manual.py
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from crm.services.evolution_api import EvolutionService
from crm.models import Lead, Oportunidade, WhatsappMessage
from django.conf import settings

def test_connection():
    """Testa conexão com Evolution API"""
    print("=" * 60)
    print("TESTE DE CONEXÃO EVOLUTION API")
    print("=" * 60)

    service = EvolutionService()
    print(f"✓ URL da API: {service.base_url}")
    print(f"✓ Instância: {service.instance}")
    print(f"✓ API Key configurada: {'Sim' if service.api_key else 'Não'}")
    print()

def test_send_message(numero, texto):
    """Testa envio de mensagem"""
    print("=" * 60)
    print("TESTE DE ENVIO DE MENSAGEM")
    print("=" * 60)

    service = EvolutionService()

    try:
        formatted = service._format_number(numero)
        print(f"Número original: {numero}")
        print(f"Número formatado: {formatted}")
        print()
        print(f"Enviando mensagem: '{texto}'")
        print()

        result = service.send_text(numero, texto)

        print("✓ MENSAGEM ENVIADA COM SUCESSO!")
        print(f"Resposta da API: {result}")
        print()

    except Exception as e:
        print(f"✗ ERRO ao enviar mensagem: {str(e)}")
        import traceback
        traceback.print_exc()
        print()

def test_lead_integration():
    """Testa integração com Leads"""
    print("=" * 60)
    print("TESTE DE INTEGRAÇÃO COM LEADS")
    print("=" * 60)

    leads_com_telefone = Lead.objects.exclude(telefone__isnull=True).exclude(telefone='')[:5]

    if not leads_com_telefone.exists():
        print("⚠ Nenhum lead com telefone encontrado no banco")
        print()
        return

    print(f"✓ Encontrados {leads_com_telefone.count()} leads com telefone:")
    for lead in leads_com_telefone:
        print(f"  - {lead.nome}: {lead.telefone}")
    print()

    # Verificar mensagens vinculadas
    total_msgs = WhatsappMessage.objects.filter(lead__isnull=False).count()
    print(f"✓ Total de mensagens vinculadas a leads: {total_msgs}")
    print()

def test_oportunidade_integration():
    """Testa integração com Oportunidades"""
    print("=" * 60)
    print("TESTE DE INTEGRAÇÃO COM OPORTUNIDADES")
    print("=" * 60)

    opps_com_contato = Oportunidade.objects.filter(
        contato_principal__isnull=False
    ).select_related('contato_principal')[:5]

    if not opps_com_contato.exists():
        print("⚠ Nenhuma oportunidade com contato encontrada no banco")
        print()
        return

    print(f"✓ Encontradas {opps_com_contato.count()} oportunidades com contato:")
    for opp in opps_com_contato:
        telefone = opp.contato_principal.telefone if opp.contato_principal else 'N/A'
        print(f"  - {opp.nome}: {telefone}")
    print()

    # Verificar mensagens vinculadas
    total_msgs = WhatsappMessage.objects.filter(oportunidade__isnull=False).count()
    print(f"✓ Total de mensagens vinculadas a oportunidades: {total_msgs}")
    print()

def menu():
    """Menu interativo"""
    print("\n" + "=" * 60)
    print("TESTES WHATSAPP - EVOLUTION API")
    print("=" * 60)
    print("1. Testar conexão")
    print("2. Testar envio de mensagem")
    print("3. Verificar integração com Leads")
    print("4. Verificar integração com Oportunidades")
    print("5. Executar todos os testes")
    print("0. Sair")
    print("=" * 60)

    opcao = input("\nEscolha uma opção: ").strip()

    if opcao == '1':
        test_connection()
    elif opcao == '2':
        numero = input("Digite o número (ex: 11999999999): ").strip()
        texto = input("Digite a mensagem: ").strip()
        if numero and texto:
            test_send_message(numero, texto)
        else:
            print("⚠ Número e texto são obrigatórios")
    elif opcao == '3':
        test_lead_integration()
    elif opcao == '4':
        test_oportunidade_integration()
    elif opcao == '5':
        test_connection()
        test_lead_integration()
        test_oportunidade_integration()
    elif opcao == '0':
        print("\nEncerrando...")
        sys.exit(0)
    else:
        print("\n⚠ Opção inválida")

    # Repetir menu
    menu()

if __name__ == '__main__':
    try:
        menu()
    except KeyboardInterrupt:
        print("\n\nEncerrando...")
        sys.exit(0)
