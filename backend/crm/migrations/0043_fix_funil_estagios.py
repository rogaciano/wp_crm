"""
Data migration: Corrige dados de funis e estágios.
- Estágio "Descartado" → tipo PERDIDO
- Funil "Pernambuco Pós-Venda" → remove estágios de vendas, adiciona estágios de pós-venda
- Move oportunidades órfãs para "Aguardando Onboarding"
"""
from django.db import migrations


def fix_funil_estagios(apps, schema_editor):
    EstagioFunil = apps.get_model('crm', 'EstagioFunil')
    FunilEstagio = apps.get_model('crm', 'FunilEstagio')
    Funil = apps.get_model('crm', 'Funil')
    Oportunidade = apps.get_model('crm', 'Oportunidade')

    # 1. Descartado → PERDIDO
    EstagioFunil.objects.filter(nome='Descartado').update(tipo='PERDIDO')

    # 2. Corrigir funil "Pernambuco Pós-Venda"
    try:
        funil_pe_pv = Funil.objects.get(nome='Pernambuco Pós-Venda', tipo='POS_VENDA')
    except Funil.DoesNotExist:
        return  # Funil não existe, nada a fazer

    # Estágios incorretos para pós-venda
    estagios_incorretos = [
        'Agendado', 'Contato Realizado', 'Descartado',
        'Tentativa de Contato', 'Fechado - Ganho',
    ]

    # Pegar o estágio "Aguardando Onboarding" para reatribuir oportunidades órfãs
    estagio_onboarding = EstagioFunil.objects.filter(nome='Aguardando Onboarding').first()
    if not estagio_onboarding:
        return

    # Mover oportunidades que estão em estágios incorretos
    estagios_a_remover = EstagioFunil.objects.filter(nome__in=estagios_incorretos)
    Oportunidade.objects.filter(
        funil=funil_pe_pv,
        estagio__in=estagios_a_remover,
    ).update(estagio=estagio_onboarding)

    # Remover vínculos incorretos
    FunilEstagio.objects.filter(
        funil=funil_pe_pv,
        estagio__nome__in=estagios_incorretos,
    ).delete()

    # 3. Criar/vincular estágios corretos de pós-venda
    novos_estagios = [
        ('Aguardando Onboarding', 'ABERTO', '#3B82F6', 1, True),
        ('Implantação', 'ABERTO', '#F59E0B', 2, False),
        ('Acompanhamento', 'ABERTO', '#8B5CF6', 3, False),
        ('Cliente Ativo', 'GANHO', '#10B981', 4, False),
        ('Churn', 'PERDIDO', '#EF4444', 5, False),
    ]

    for nome, tipo, cor, ordem, is_padrao in novos_estagios:
        estagio, _ = EstagioFunil.objects.get_or_create(
            nome=nome,
            defaults={'tipo': tipo, 'cor': cor},
        )
        FunilEstagio.objects.update_or_create(
            funil=funil_pe_pv,
            estagio=estagio,
            defaults={'ordem': ordem, 'is_padrao': is_padrao},
        )

    # Garantir que só 1 estágio é padrão
    FunilEstagio.objects.filter(funil=funil_pe_pv).exclude(
        estagio=estagio_onboarding
    ).update(is_padrao=False)


def reverse_migration(apps, schema_editor):
    # Reversão: voltar Descartado para ABERTO
    EstagioFunil = apps.get_model('crm', 'EstagioFunil')
    EstagioFunil.objects.filter(nome='Descartado').update(tipo='ABERTO')


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0042_merge_branches'),
    ]

    operations = [
        migrations.RunPython(fix_funil_estagios, reverse_migration),
    ]
