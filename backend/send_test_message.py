import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from crm.services.evolution_api import EvolutionService

# --- CONFIGURAÇÃO ---
# Coloque o número aqui com DDI e DDD (ex: 5511988887777)
NUMERO_TESTE = "5581999216560" 
MENSAGEM = "Teste de integração CRM - WhatsApp está OK! 🚀"
# --------------------

def send_test():
    if NUMERO_TESTE == "SUBSTITUA_PELO_NUMERO":
        print("\nERRO: Você precisa editar este arquivo e colocar um número válido na variável NUMERO_TESTE.")
        return

    service = EvolutionService()
    print(f"\nEnviando mensagem para: {NUMERO_TESTE}")
    try:
        result = service.send_text(NUMERO_TESTE, MENSAGEM)
        print("\n✅ Sucesso! Resposta da API:")
        print(result)
    except Exception as e:
        print(f"\n❌ Erro ao enviar: {str(e)}")

if __name__ == "__main__":
    send_test()
