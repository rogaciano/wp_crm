"""
Signals para capturar ações e criar logs automaticamente
"""
from django.db.models.signals import post_save, post_delete, pre_save, m2m_changed
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from .models import Log, Conta, Contato, Oportunidade, Atividade, TipoRedeSocial, ContatoRedeSocial, OportunidadeAdicional
from .middleware import get_current_request, get_current_user
import json


# Lista de modelos que queremos auditar
MODELOS_AUDITADOS = [Conta, Contato, Oportunidade, Atividade, ContatoRedeSocial, OportunidadeAdicional]


@receiver(pre_save)
def capture_old_values(sender, instance, **kwargs):
    """
    Captura os valores anteriores antes de salvar para comparação posterior.
    """
    # Ignora o próprio modelo Log
    if sender == Log:
        return
    
    # Verifica se o modelo está na lista de auditados
    if sender not in MODELOS_AUDITADOS:
        return
    
    # Só captura valores para objetos existentes (UPDATE, não CREATE)
    if instance.pk:
        try:
            # Busca o objeto original do banco de dados
            old_instance = sender.objects.get(pk=instance.pk)
            
            # Armazena os valores antigos no objeto
            instance._old_values = {}
            for field in instance._meta.fields:
                field_name = field.name
                old_value = getattr(old_instance, field_name, None)
                instance._old_values[field_name] = old_value
        except sender.DoesNotExist:
            # Objeto novo, não existe no banco ainda
            instance._old_values = {}
    else:
        # Objeto novo
        instance._old_values = {}


def get_client_ip(request):
    """Obtém o IP do cliente da requisição"""
    if not request:
        return None

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """Obtém o user agent do navegador"""
    if not request:
        return None
    return request.META.get('HTTP_USER_AGENT', '')


def get_changed_fields(instance, created):
    """
    Retorna um dicionário com os campos que foram alterados.
    Para criação, retorna todos os campos.
    """
    if created:
        # Para objetos criados, captura todos os campos não vazios
        changes = {}
        for field in instance._meta.fields:
            field_name = field.name
            # Ignora campos de auditoria e IDs
            if field_name in ['id', 'data_criacao', 'data_atualizacao', 'criado_por', 'atualizado_por']:
                continue

            value = getattr(instance, field_name, None)
            if value is not None:
                # Converte valores especiais para string
                if hasattr(value, 'pk'):  # ForeignKey
                    changes[field_name] = {'antes': None, 'depois': str(value)}
                else:
                    changes[field_name] = {'antes': None, 'depois': str(value)}
        return changes

    # Para atualizações, compara com valores anteriores
    changes = {}
    if hasattr(instance, '_old_values'):
        for field in instance._meta.fields:
            field_name = field.name
            if field_name in ['id', 'data_criacao', 'data_atualizacao']:
                continue

            old_value = instance._old_values.get(field_name)
            new_value = getattr(instance, field_name, None)

            # Converte para string para comparação
            old_str = str(old_value) if old_value is not None else None
            new_str = str(new_value) if new_value is not None else None

            if old_str != new_str:
                changes[field_name] = {
                    'antes': old_str,
                    'depois': new_str
                }

    return changes


@receiver(post_save)
def log_model_save(sender, instance, created, **kwargs):
    """
    Captura sinais de post_save para modelos auditados
    """
    # Ignora o próprio modelo Log para evitar loop infinito
    if sender == Log:
        return

    # Verifica se o modelo está na lista de auditados
    if sender not in MODELOS_AUDITADOS:
        return

    # Obtém usuário e request do thread-local storage
    user = get_current_user()
    request = get_current_request()

    # Obtém as alterações
    alteracoes = get_changed_fields(instance, created)

    # Cria o log
    Log.objects.create(
        usuario=user,
        acao=Log.ACAO_CREATE if created else Log.ACAO_UPDATE,
        modelo=sender.__name__,
        objeto_id=instance.pk,
        objeto_repr=str(instance),
        alteracoes=alteracoes if alteracoes else None,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        observacao=f"{'Criado' if created else 'Atualizado'} via sistema"
    )


@receiver(post_delete)
def log_model_delete(sender, instance, **kwargs):
    """
    Captura sinais de post_delete para modelos auditados
    """
    # Ignora o próprio modelo Log
    if sender == Log:
        return

    # Verifica se o modelo está na lista de auditados
    if sender not in MODELOS_AUDITADOS:
        return

    # Obtém usuário e request do thread-local storage
    user = get_current_user()
    request = get_current_request()

    # Cria o log de exclusão
    Log.objects.create(
        usuario=user,
        acao=Log.ACAO_DELETE,
        modelo=sender.__name__,
        objeto_id=instance.pk,
        objeto_repr=str(instance),
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        observacao="Excluído via sistema"
    )


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """
    Captura login de usuário
    """
    Log.objects.create(
        usuario=user,
        acao=Log.ACAO_LOGIN,
        modelo='User',
        objeto_id=user.pk,
        objeto_repr=user.get_full_name() or user.username,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        observacao="Login realizado com sucesso"
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """
    Captura logout de usuário
    """
    if user:  # user pode ser None em alguns casos
        Log.objects.create(
            usuario=user,
            acao=Log.ACAO_LOGOUT,
            modelo='User',
            objeto_id=user.pk,
            objeto_repr=user.get_full_name() or user.username,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            observacao="Logout realizado"
        )


@receiver(m2m_changed)
def log_m2m_changes(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    Captura alterações em campos ManyToMany (Contatos e Empresas na Oportunidade)
    """
    if action not in ['post_add', 'post_remove', 'post_clear']:
        return

    # Se instancia não é Oportunidade, pode ser o reverso (ex: adicionando oportunidade no contato)
    # Vamos focar apenas quando o alvo é Oportunidade para simplificar o log na timeline da Oportunidade
    if not isinstance(instance, Oportunidade):
        return

    # Verifica qual campo mudou
    campo = None
    if sender == Oportunidade.contatos.through:
        campo = 'Contatos'
        NomeModel = Contato
    elif sender == Oportunidade.empresas.through:
        campo = 'Empresas'
        NomeModel = Conta
    else:
        return

    user = get_current_user()
    request = get_current_request()
    
    # Busca nomes dos objetos afetados
    nomes = []
    if pk_set:
        objs = NomeModel.objects.filter(pk__in=pk_set)
        if NomeModel == Contato:
            nomes = [o.nome for o in objs]
        else:
            nomes = [o.nome_empresa for o in objs]
    
    nomes_str = ", ".join(nomes)
    
    acao_verbose = ""
    if action == 'post_add':
        acao_verbose = "Adicionou"
    elif action == 'post_remove':
        acao_verbose = "Removeu"
    elif action == 'post_clear':
        acao_verbose = "Removeu todos"
        nomes_str = f"os {campo.lower()}"

    observacao = f"{acao_verbose} {campo}: {nomes_str}"

    Log.objects.create(
        usuario=user,
        acao=Log.ACAO_UPDATE,
        modelo='Oportunidade',
        objeto_id=instance.pk,
        objeto_repr=str(instance),
        alteracoes={campo: {'antes': None, 'depois': observacao}},
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        observacao=observacao
    )
@receiver(post_save, sender=Oportunidade)
def automatizar_pos_venda_suporte(sender, instance, created, **kwargs):
    """
    Quando uma oportunidade é marcada como GANHA, cria automaticamente 
    registros nos funis de Pós-Venda e Suporte.
    """
    from .models import Funil, EstagioFunil, FunilEstagio
    # Verifica se o estágio atual é do tipo GANHO
    if instance.estagio.tipo == 'GANHO':
        # Verifica se já era GANHO antes para evitar duplicidade (usando o cache do sinal capture_old_values)
        if hasattr(instance, '_old_values'):
            # O capture_old_values armazena o objeto completo para campos ForeignKey
            old_estagio = instance._old_values.get('estagio')
            if old_estagio and getattr(old_estagio, 'tipo', None) == 'GANHO':
                return # Já era ganho, ignora

        # 1. Buscar ou Criar Funil de Pós-Venda
        funil_pos = Funil.objects.filter(tipo=Funil.TIPO_POS_VENDA).first()
        if not funil_pos:
            funil_pos = Funil.objects.create(
                tipo=Funil.TIPO_POS_VENDA,
                nome='Esteira de Pós-Venda'
            )
            # Cria estágio inicial padrão
            est_pos = EstagioFunil.objects.get_or_create(nome='Aguardando Onboarding', defaults={'tipo': 'ABERTO'})[0]
            FunilEstagio.objects.create(funil=funil_pos, estagio=est_pos, ordem=0, is_padrao=True)
        
        # 2. Buscar ou Criar Funil de Suporte
        funil_suporte = Funil.objects.filter(tipo=Funil.TIPO_SUPORTE).first()
        if not funil_suporte:
            funil_suporte = Funil.objects.create(
                tipo=Funil.TIPO_SUPORTE,
                nome='Tickets de Suporte'
            )
            # Cria estágio inicial padrão
            est_sup = EstagioFunil.objects.get_or_create(nome='Triagem de Suporte', defaults={'tipo': 'ABERTO'})[0]
            FunilEstagio.objects.create(funil=funil_suporte, estagio=est_sup, ordem=0, is_padrao=True)
        
        # Garantir estágios iniciais para esses funis
        def get_estagio_inicial(funil):
            fe = FunilEstagio.objects.filter(funil=funil, is_padrao=True).first()
            if not fe:
                fe = FunilEstagio.objects.filter(funil=funil).order_by('ordem').first()
            if fe:
                return fe.estagio
            return None

        estagio_pos = get_estagio_inicial(funil_pos)
        estagio_sup = get_estagio_inicial(funil_suporte)
        
        # Se não tiver estágios, o sistema pode dar erro ao criar a oportunidade
        # Idealmente esses funis já devem ter sido configurados via Admin
        
        if estagio_pos:
            # Verifica se já existe pós-venda para esta oportunidade (evitar loops)
            if not Oportunidade.objects.filter(
                conta=instance.conta, 
                funil=funil_pos,
                nome__icontains=f"Pós-Venda: {instance.nome}"
            ).exists():
                nova_opp = Oportunidade.objects.create(
                    nome=f"Pós-Venda: {instance.nome}",
                    conta=instance.conta,
                    contato_principal=instance.contato_principal,
                    funil=funil_pos,
                    estagio=estagio_pos,
                    proprietario=instance.proprietario, # Vendedor
                    valor_estimado=instance.valor_estimado,
                    canal=instance.canal
                )
                # Copia contatos secundários (M2M)
                if instance.contatos.exists():
                    nova_opp.contatos.set(instance.contatos.all())

        if estagio_sup:
            # Verifica se já existe suporte para esta oportunidade
            if not Oportunidade.objects.filter(
                conta=instance.conta, 
                funil=funil_suporte,
                nome__icontains=f"Suporte: {instance.nome}"
            ).exists():
                nova_sup = Oportunidade.objects.create(
                    nome=f"Suporte: {instance.nome}",
                    conta=instance.conta,
                    contato_principal=instance.contato_principal,
                    funil=funil_suporte,
                    estagio=estagio_sup,
                    proprietario=instance.proprietario, # Ajustar para técnico se houver campo
                    valor_estimado=0,
                    canal=instance.canal
                )
                # Copia contatos secundários (M2M)
                if instance.contatos.exists():
                    nova_sup.contatos.set(instance.contatos.all())
