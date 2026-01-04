"""
Teste minimalista - escreve em arquivo
"""
import os
import sys

LOG_FILE = r"E:\projetos\crm_wp\backend\debug_result.log"

def log(msg):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(str(msg) + '\n')
    print(msg)

# Limpa arquivo
with open(LOG_FILE, 'w', encoding='utf-8') as f:
    f.write('')

log("=" * 60)
log("INICIANDO TESTE")
log("=" * 60)

try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    import django
    django.setup()
    log("Django configurado OK")
    
    from django.utils import timezone
    from django.conf import settings
    from crm.models import WhatsappMessage, Lead
    from crm.services.evolution_api import EvolutionService
    import uuid
    
    log(f"EVOLUTION_INSTANCE_ID = {settings.EVOLUTION_INSTANCE_ID}")
    
    # Buscar lead
    lead = Lead.objects.filter(telefone__icontains="81999216560").first()
    log(f"Lead encontrado: {lead}")
    
    # Testar envio
    service = EvolutionService()
    number = "81999216560"
    text = f"Debug test {timezone.now().strftime('%H:%M:%S')}"
    
    log(f"Enviando para {number}...")
    result = service.send_text(number, text)
    log(f"Resultado: {result}")
    
    # Extrair ID
    msg_id = None
    if isinstance(result, dict):
        if 'key' in result and isinstance(result['key'], dict):
            msg_id = result['key'].get('id')
    
    if not msg_id:
        msg_id = f"local_{uuid.uuid4().hex[:20]}"
    log(f"msg_id = {msg_id}")
    
    formatted = service._format_number(number)
    log(f"formatted = {formatted}")
    
    # Salvar
    lead_id = lead.id if lead else None
    log(f"lead_id = {lead_id}")
    
    log("Criando WhatsappMessage...")
    msg = WhatsappMessage.objects.create(
        id_mensagem=msg_id,
        instancia=settings.EVOLUTION_INSTANCE_ID,
        de_mim=True,
        numero_remetente=settings.EVOLUTION_INSTANCE_ID,
        numero_destinatario=formatted,
        texto=text,
        timestamp=timezone.now(),
        lead_id=lead_id,
        oportunidade_id=None
    )
    log(f"SUCESSO! msg.id = {msg.id}")
    
except Exception as e:
    import traceback
    log(f"ERRO: {e}")
    log(traceback.format_exc())

log("=" * 60)
log("FIM")
