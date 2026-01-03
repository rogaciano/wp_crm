import os
import django
import sys

# Set up Django environment
sys.path.append('e:/projetos/crm_wp/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from crm.models import Funil, EstagioFunil, User, Oportunidade, Lead

def populate():
    # 1. Create Funnels
    sdr_funil, _ = Funil.objects.get_or_create(
        nome='Funil SDR',
        defaults={'tipo': Funil.TIPO_LEAD}
    )
    vendas_funil, _ = Funil.objects.get_or_create(
        nome='Funil de Vendas',
        defaults={'tipo': Funil.TIPO_OPORTUNIDADE}
    )
    
    # Associate all users to both funnels for now
    users = User.objects.all()
    sdr_funil.usuarios.set(users)
    vendas_funil.usuarios.set(users)
    
    # 2. Setup SDR Stages
    sdr_stages = [
        ('Novo Lead', 10, '#3B82F6', True), # Initial
        ('Tentativa de Contato', 20, '#F59E0B', False),
        ('Contato Realizado', 30, '#10B981', False),
        ('Agendado', 40, '#8B5CF6', False),
        ('Qualificado', 50, '#10B981', False),
        ('Descartado', 60, '#EF4444', False),
    ]
    
    for nome, ordem, cor, is_padrao in sdr_stages:
        EstagioFunil.objects.get_or_create(
            funil=sdr_funil,
            nome=nome,
            defaults={'ordem': ordem, 'cor': cor, 'is_padrao': is_padrao}
        )
    
    # 3. Setup Vendas Stages (Move existing ones or create new)
    # Existing stages don't have a funnel yet. Let's find them.
    existing_stages = EstagioFunil.objects.filter(funil__isnull=True)
    if existing_stages.exists():
        existing_stages.update(funil=vendas_funil)
        # Set first stage as default if none set
        first = existing_stages.order_by('ordem').first()
        if first:
            first.is_padrao = True
            first.save()
    else:
        vendas_stages = [
            ('Prospecção', 10, '#3B82F6', True),
            ('Qualificação', 20, '#6366F1', False),
            ('Proposta', 30, '#F59E0B', False),
            ('Negociação', 40, '#8B5CF6', False),
            ('Fechado - Ganho', 50, '#10B981', False),
            ('Fechado - Perdido', 60, '#EF4444', False),
        ]
        for nome, ordem, cor, is_padrao in vendas_stages:
            EstagioFunil.objects.get_or_create(
                funil=vendas_funil,
                nome=nome,
                defaults={'ordem': ordem, 'cor': cor, 'is_padrao': is_padrao}
            )

    # 4. Migrate existing Leads and Opportunities
    # Leads
    default_sdr_stage = EstagioFunil.objects.filter(funil=sdr_funil, is_padrao=True).first()
    Lead.objects.filter(funil__isnull=True).update(funil=sdr_funil, estagio=default_sdr_stage)
    
    # Opportunities
    Oportunidade.objects.filter(funil__isnull=True).update(funil=vendas_funil)
    
    print("População de funis concluída com sucesso!")

if __name__ == '__main__':
    populate()
