"""
Script para verificar e criar estágios se necessário
Execute: python manage.py shell < check_estagios.py
"""

from crm.models import EstagioFunil

print("=== Verificando Estágios do Funil ===\n")

# Verificar quantos estágios existem
total = EstagioFunil.objects.count()
print(f"Total de estágios no banco: {total}")

if total > 0:
    print("\nEstágios existentes:")
    for estagio in EstagioFunil.objects.all().order_by('nome'):
        print(f"  • {estagio.nome} ({estagio.tipo}) - Cor: {estagio.cor}")
else:
    print("\n⚠️ Nenhum estágio encontrado! Criando estágios iniciais...")
    
    estagios_data = [
        {"nome": "Prospecção", "tipo": "ABERTO", "cor": "#3B82F6"},
        {"nome": "Qualificação", "tipo": "ABERTO", "cor": "#8B5CF6"},
        {"nome": "Proposta", "tipo": "ABERTO", "cor": "#EC4899"},
        {"nome": "Negociação", "tipo": "ABERTO", "cor": "#F59E0B"},
        {"nome": "Fechado - Ganho", "tipo": "GANHO", "cor": "#10B981"},
        {"nome": "Fechado - Perdido", "tipo": "PERDIDO", "cor": "#EF4444"},
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
    
    print("\n✅ Estágios criados com sucesso!")

print("\n=== Verificação concluída ===")

