"""
Script para normalizar todos os telefones existentes no banco de dados.
Execute com: python manage.py shell < normalize_phones.py
"""
import os
import re
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()

from crm.models import Lead, Contato


def normalize_phone_brazil(phone):
    """Normaliza telefone para formato 55DDDNNNNNNNNN (13 dígitos)"""
    if not phone:
        return ''
    
    digits = re.sub(r'\D', '', str(phone))
    
    if not digits:
        return ''
    
    # Remove DDI 55 se existir
    if digits.startswith('55') and len(digits) >= 12:
        digits = digits[2:]
    
    if len(digits) == 10:
        ddd = digits[:2]
        numero = digits[2:]
        digits = ddd + '9' + numero
    elif len(digits) == 11:
        pass
    elif len(digits) == 8:
        return ''
    else:
        return ''
    
    return '55' + digits


print("=" * 60)
print("NORMALIZAÇÃO DE TELEFONES")
print("=" * 60)

# Normaliza Leads
print("\n📋 LEADS:")
leads_updated = 0
for lead in Lead.objects.all():
    if lead.telefone:
        old = lead.telefone
        new = normalize_phone_brazil(old)
        if new and new != old:
            print(f"  {lead.nome}: '{old}' → '{new}'")
            lead.telefone = new
            lead.save(update_fields=['telefone'])
            leads_updated += 1
        elif not new and old:
            print(f"  ⚠️ {lead.nome}: '{old}' → INVÁLIDO (mantido)")

print(f"  ✅ {leads_updated} leads atualizados")

# Normaliza Contatos
print("\n📋 CONTATOS:")
contatos_updated = 0
for contato in Contato.objects.all():
    updated = False
    
    if contato.telefone:
        old = contato.telefone
        new = normalize_phone_brazil(old)
        if new and new != old:
            print(f"  {contato.nome} (tel): '{old}' → '{new}'")
            contato.telefone = new
            updated = True
    
    if contato.celular:
        old = contato.celular
        new = normalize_phone_brazil(old)
        if new and new != old:
            print(f"  {contato.nome} (cel): '{old}' → '{new}'")
            contato.celular = new
            updated = True
    
    if updated:
        contato.save(update_fields=['telefone', 'celular'])
        contatos_updated += 1

print(f"  ✅ {contatos_updated} contatos atualizados")

print("\n" + "=" * 60)
print("FINALIZADO")
print("=" * 60)
