"""
Script para reprocessar vinculação de mensagens do WhatsApp com Leads/Oportunidades.
Execute na VPS com: python manage.py shell < relink_messages.py
Ou cole o conteúdo no shell interativo.
"""
import os
import django

# Se executar como script standalone
if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

from crm.models import WhatsappMessage, Lead
from crm.services.evolution_api import EvolutionService

print("=" * 60)
print("REPROCESSAMENTO DE VINCULAÇÃO DE MENSAGENS")
print("=" * 60)

# Diagnóstico inicial
total_msgs = WhatsappMessage.objects.count()
incoming = WhatsappMessage.objects.filter(de_mim=False)
unread = incoming.filter(lida=False)
unlinked = unread.filter(lead__isnull=True, oportunidade__isnull=True)

print(f"\n📊 DIAGNÓSTICO INICIAL:")
print(f"   Total de mensagens: {total_msgs}")
print(f"   Mensagens recebidas: {incoming.count()}")
print(f"   Não lidas: {unread.count()}")
print(f"   Não vinculadas (órfãs): {unlinked.count()}")

# Reprocessa TODAS as mensagens para garantir vinculação correta
print(f"\n🔄 Reprocessando vinculações...")

updated_count = 0
for msg in WhatsappMessage.objects.all():
    old_lead = msg.lead_id
    old_opp = msg.oportunidade_id
    
    EvolutionService.identify_and_link_message(msg)
    
    if msg.lead_id != old_lead or msg.oportunidade_id != old_opp:
        updated_count += 1

print(f"✅ {updated_count} mensagens atualizadas")

# Diagnóstico final
unlinked_after = WhatsappMessage.objects.filter(
    de_mim=False, lida=False, lead__isnull=True, oportunidade__isnull=True
)

print(f"\n📊 DIAGNÓSTICO FINAL:")
print(f"   Mensagens órfãs restantes: {unlinked_after.count()}")

if unlinked_after.count() > 0:
    print(f"\n⚠️  Mensagens que ainda não puderam ser vinculadas:")
    for msg in unlinked_after[:10]:
        print(f"   • De: {msg.numero_remetente} - '{msg.texto[:40]}...'")
    
    # Lista os leads e seus telefones para comparação
    print(f"\n📋 LEADS CADASTRADOS:")
    for lead in Lead.objects.all()[:20]:
        print(f"   • {lead.nome}: {lead.telefone}")

# Mostra leads com notificações
print(f"\n🔔 LEADS COM NOTIFICAÇÕES:")
for lead in Lead.objects.all():
    count = lead.mensagens_whatsapp.filter(de_mim=False, lida=False).count()
    if count > 0:
        print(f"   ✅ {lead.nome}: {count} mensagem(ns) não lida(s)")

print("\n" + "=" * 60)
print("FINALIZADO")
print("=" * 60)
