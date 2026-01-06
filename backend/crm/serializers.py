"""
Serializers para a API do CRM
"""
import re
from rest_framework import serializers
from django.db import transaction
from django.contrib.auth.password_validation import validate_password
from .models import (
    Canal, User, Lead, Conta, Contato, TipoContato, TipoRedeSocial, ContatoRedeSocial,
    Funil, EstagioFunil, FunilEstagio, Oportunidade, Atividade,
    DiagnosticoPilar, DiagnosticoPergunta, DiagnosticoResposta, DiagnosticoResultado, 
    Plano, PlanoAdicional, OportunidadeAdicional, WhatsappMessage
)


def normalize_phone_brazil(phone: str) -> str:
    """
    Normaliza um telefone CELULAR brasileiro para o formato 55DDDNNNNNNNNN (13 dígitos).
    Usado para celulares - SEMPRE adiciona o 9º dígito se não tiver.

    Aceita formatos como:
    - (81) 9 9921-6560
    - 81999216560
    - +55 81 999216560
    - 5581999216560

    Retorna:
    - 5581999216560 (sempre 13 dígitos com DDI e 9º dígito)
    - String vazia se inválido
    """
    if not phone:
        return ''

    # Remove tudo que não é dígito
    digits = re.sub(r'\D', '', str(phone))

    if not digits:
        return ''

    # Remove DDI 55 se existir para processar
    if digits.startswith('55') and len(digits) >= 12:
        digits = digits[2:]

    # Agora digits deve ter DDD + número (10 ou 11 dígitos)
    if len(digits) == 10:
        # Formato antigo sem 9: adiciona o 9 (para celular)
        ddd = digits[:2]
        numero = digits[2:]
        digits = ddd + '9' + numero
    elif len(digits) == 11:
        # Formato com 9: ok
        pass
    elif len(digits) == 8:
        # Só o número sem DDD: não podemos assumir DDD
        return ''
    else:
        # Formato irreconhecível
        return ''

    # Adiciona DDI 55
    return '55' + digits


def normalize_landline_brazil(phone: str) -> str:
    """
    Normaliza um telefone FIXO brasileiro.
    Aceita 10 dígitos (DDD + 8 dígitos) ou 11 dígitos (com 9).
    NÃO força o 9º dígito - mantém como está.

    Aceita formatos como:
    - (81) 3333-4444 (fixo, 8 dígitos)
    - (81) 9 3333-4444 (pode ter 9 no início)
    - 8133334444
    - 81933334444

    Retorna:
    - 558133334444 (12 dígitos se fixo sem 9)
    - 5581933334444 (13 dígitos se tiver o 9)
    - String vazia se inválido
    """
    if not phone:
        return ''

    # Remove tudo que não é dígito
    digits = re.sub(r'\D', '', str(phone))

    if not digits:
        return ''

    # Remove DDI 55 se existir para processar
    if digits.startswith('55'):
        if len(digits) >= 12:
            digits = digits[2:]

    # Aceita 10 dígitos (fixo) ou 11 dígitos (com 9)
    if len(digits) == 10 or len(digits) == 11:
        # Adiciona DDI 55 e retorna
        return '55' + digits
    elif len(digits) == 8:
        # Só o número sem DDD: não podemos assumir DDD
        return ''
    else:
        # Formato irreconhecível
        return ''


def format_phone_display(phone: str) -> str:
    """
    Formata um telefone normalizado para exibição.
    - Celular (13 dígitos): (81) 9 9921-6560
    - Fixo (12 dígitos): (81) 3333-4444
    """
    if not phone:
        return ''

    if len(phone) == 13:
        # Celular: 5581999216560 -> (81) 9 9921-6560
        ddd = phone[2:4]
        p1 = phone[4:5]   # 9
        p2 = phone[5:9]   # 9921
        p3 = phone[9:13]  # 6560
        return f"({ddd}) {p1} {p2}-{p3}"
    elif len(phone) == 12:
        # Fixo: 558133334444 -> (81) 3333-4444
        ddd = phone[2:4]
        p1 = phone[4:8]   # 3333
        p2 = phone[8:12]  # 4444
        return f"({ddd}) {p1}-{p2}"
    else:
        # Formato desconhecido, retorna como está
        return phone


class CanalSerializer(serializers.ModelSerializer):
    responsavel_nome = serializers.SerializerMethodField()
    total_vendedores = serializers.SerializerMethodField()
    
    def get_responsavel_nome(self, obj):
        return obj.responsavel.get_full_name() if obj.responsavel else "N/A"
    
    class Meta:
        model = Canal
        fields = ['id', 'nome', 'responsavel', 'responsavel_nome', 'total_vendedores', 'data_criacao']
        read_only_fields = ['data_criacao']
    
    def get_total_vendedores(self, obj):
        return obj.vendedores.count()


class UserSerializer(serializers.ModelSerializer):
    canal_nome = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    
    def get_canal_nome(self, obj):
        return obj.canal.nome if obj.canal else "N/A"
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username
    
    def get_avatar_url(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None
        
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'perfil', 'canal', 'canal_nome', 'telefone', 'avatar', 'avatar_url',
            'password', 'is_active', 'date_joined'
        ]
        read_only_fields = ['date_joined']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


# Serializers do Diagnóstico (Precisam vir antes do LeadSerializer)

class DiagnosticoRespostaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagnosticoResposta
        fields = ['id', 'texto', 'pontuacao', 'feedback']


class DiagnosticoPerguntaSerializer(serializers.ModelSerializer):
    respostas = DiagnosticoRespostaSerializer(many=True, read_only=True)
    
    class Meta:
        model = DiagnosticoPergunta
        fields = ['id', 'texto', 'ordem', 'ajuda', 'respostas']


class DiagnosticoPilarSerializer(serializers.ModelSerializer):
    perguntas = DiagnosticoPerguntaSerializer(many=True, read_only=True)
    
    class Meta:
        model = DiagnosticoPilar
        fields = ['id', 'nome', 'slug', 'descricao', 'ordem', 'cor', 'perguntas']


class DiagnosticoResultadoSerializer(serializers.ModelSerializer):
    lead_nome = serializers.CharField(source='lead.nome', read_only=True)
    
    class Meta:
        model = DiagnosticoResultado
        fields = [
            'id', 'lead', 'lead_nome', 'data_conclusao',
            'respostas_detalhadas', 'pontuacao_por_pilar', 'analise_ia'
        ]
        read_only_fields = ['data_conclusao']


class DiagnosticoPublicSubmissionSerializer(serializers.Serializer):
    """Serializer para submissão pública do diagnóstico e criação de Lead"""
    nome = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    telefone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    empresa = serializers.CharField(max_length=255, required=False, allow_blank=True)
    
    # Lista de IDs das respostas escolhidas
    respostas_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )


class LeadSerializer(serializers.ModelSerializer):
    proprietario_nome = serializers.CharField(source='proprietario.get_full_name', read_only=True)
    proprietario_canal = serializers.SerializerMethodField()
    proprietario = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    diagnosticos = DiagnosticoResultadoSerializer(many=True, read_only=True)
    funil_nome = serializers.CharField(source='funil.nome', read_only=True)
    estagio_nome = serializers.CharField(source='estagio.nome', read_only=True)
    estagio_cor = serializers.CharField(source='estagio.cor', read_only=True)
    canal_nome = serializers.CharField(source='canal.nome', read_only=True)
    
    whatsapp_nao_lidas = serializers.SerializerMethodField()
    telefone_formatado = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = [
            'id', 'nome', 'email', 'telefone', 'telefone_formatado', 'empresa', 'cargo',
            'fonte', 'status', 'funil', 'funil_nome', 'estagio', 'estagio_nome', 'estagio_cor',
            'canal', 'canal_nome',
            'notas', 'proprietario', 'proprietario_nome', 'proprietario_canal',
            'diagnosticos', 'whatsapp_nao_lidas', 'data_criacao', 'data_atualizacao'
        ]
        read_only_fields = ['data_criacao', 'data_atualizacao', 'proprietario', 'diagnosticos', 'whatsapp_nao_lidas', 'telefone_formatado']

    def get_whatsapp_nao_lidas(self, obj):
        """
        Conta mensagens não lidas respeitando o canal do usuário.
        Se o lead tem canal definido, conta apenas mensagens desse canal.
        Se o usuário não é admin, conta apenas mensagens do seu canal.
        """
        mensagens_query = obj.mensagens_whatsapp.filter(lida=False, de_mim=False)

        # Se o usuário estiver disponível no contexto, filtrar por canal
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user

            # Se não é admin, precisa filtrar por canal
            if user.perfil != 'ADMIN':
                # Se o lead tem canal, usa o canal do lead
                # Se não tem, usa o canal do proprietário do lead
                canal_lead = obj.canal or (obj.proprietario.canal if obj.proprietario else None)

                # Se o canal do lead é diferente do canal do usuário, retorna 0
                if canal_lead and user.canal and canal_lead.id != user.canal.id:
                    return 0

        return mensagens_query.count()
    
    def get_proprietario_canal(self, obj):
        return obj.proprietario.canal.id if obj.proprietario and obj.proprietario.canal else None
    
    def get_telefone_formatado(self, obj):
        """Retorna o telefone formatado para exibição: (81) 9 9921-6560"""
        return format_phone_display(obj.telefone) if obj.telefone else ''
    
    def validate_telefone(self, value):
        """Valida e normaliza o telefone para formato brasileiro padrão"""
        if not value:
            return value
        
        normalized = normalize_phone_brazil(value)
        if not normalized:
            raise serializers.ValidationError(
                "Telefone inválido. Use o formato: (DDD) 9 XXXX-XXXX ou apenas os números."
            )
        return normalized

    def create(self, validated_data):
        # Define o proprietário como o usuário logado
        if 'request' in self.context and self.context['request'].user.is_authenticated:
            validated_data['proprietario'] = self.context['request'].user
        
        # Se não informou funil/estágio, busca o padrão
        if not validated_data.get('funil'):
            funil_padrao = Funil.objects.filter(tipo=Funil.TIPO_LEAD, is_active=True).first()
            if funil_padrao:
                validated_data['funil'] = funil_padrao
                if not validated_data.get('estagio'):
                    estagio_padrao = EstagioFunil.objects.filter(funil=funil_padrao, is_padrao=True).first()
                    if estagio_padrao:
                        validated_data['estagio'] = estagio_padrao
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class ContaSerializer(serializers.ModelSerializer):
    proprietario_nome = serializers.CharField(source='proprietario.get_full_name', read_only=True)
    proprietario = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    total_contatos = serializers.SerializerMethodField()
    total_oportunidades = serializers.SerializerMethodField()
    diagnosticos = DiagnosticoResultadoSerializer(many=True, read_only=True)
    
    canal_nome = serializers.CharField(source='canal.nome', read_only=True)
    
    class Meta:
        model = Conta
        fields = [
            'id', 'nome_empresa', 'cnpj', 'telefone_principal', 'email',
            'website', 'setor', 'endereco', 'cidade', 'estado', 'cep',
            'notas', 'canal', 'canal_nome', 'proprietario', 'proprietario_nome',
            'total_contatos', 'total_oportunidades', 'diagnosticos',
            'data_criacao', 'data_atualizacao'
        ]
        read_only_fields = ['data_criacao', 'data_atualizacao', 'proprietario', 'diagnosticos']
    
    def get_total_contatos(self, obj):
        return obj.contatos.count()
    
    def get_total_oportunidades(self, obj):
        return obj.oportunidades.count()
    
    def create(self, validated_data):
        validated_data['proprietario'] = self.context['request'].user
        return super().create(validated_data)


class TipoContatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoContato
        fields = ['id', 'nome', 'descricao', 'data_criacao']


class TipoRedeSocialSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoRedeSocial
        fields = ['id', 'nome', 'icone', 'cor', 'url_base', 'placeholder', 'ordem', 'ativo']


class ContatoRedeSocialSerializer(serializers.ModelSerializer):
    tipo_nome = serializers.CharField(source='tipo.nome', read_only=True)
    tipo_icone = serializers.CharField(source='tipo.icone', read_only=True)
    tipo_cor = serializers.CharField(source='tipo.cor', read_only=True)
    url_completa = serializers.CharField(read_only=True)
    
    class Meta:
        model = ContatoRedeSocial
        fields = ['id', 'tipo', 'tipo_nome', 'tipo_icone', 'tipo_cor', 'valor', 'url_completa']


class ContatoSerializer(serializers.ModelSerializer):
    proprietario_nome = serializers.CharField(source='proprietario.get_full_name', read_only=True)
    proprietario = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    conta_nome = serializers.CharField(source='conta.nome_empresa', read_only=True)
    tipo_contato_nome = serializers.CharField(source='tipo_contato.nome', read_only=True)
    canal_nome = serializers.CharField(source='canal.nome', read_only=True)
    telefone_formatado = serializers.SerializerMethodField()
    celular_formatado = serializers.SerializerMethodField()
    foto_url = serializers.SerializerMethodField()
    redes_sociais = ContatoRedeSocialSerializer(many=True, read_only=True)
    
    class Meta:
        model = Contato
        fields = [
            'id', 'nome', 'email', 'telefone', 'telefone_formatado', 'celular', 'celular_formatado', 'cargo',
            'departamento', 'chave_pix', 'foto', 'foto_url', 'tipo_contato', 'tipo_contato_nome', 'tipo',
            'conta', 'conta_nome', 'canal', 'canal_nome',
            'proprietario', 'proprietario_nome', 'notas',
            'redes_sociais',
            'data_criacao', 'data_atualizacao'
        ]
        read_only_fields = ['data_criacao', 'data_atualizacao', 'proprietario', 'telefone_formatado', 'celular_formatado', 'foto_url', 'redes_sociais']
    
    def get_foto_url(self, obj):
        if obj.foto:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.foto.url)
            return obj.foto.url
        return None
    
    def get_telefone_formatado(self, obj):
        return format_phone_display(obj.telefone) if obj.telefone else ''
    
    def get_celular_formatado(self, obj):
        return format_phone_display(obj.celular) if obj.celular else ''
    
    def validate_telefone(self, value):
        """Valida telefone FIXO - aceita com ou sem o 9º dígito"""
        if not value:
            return value
        normalized = normalize_landline_brazil(value)
        if not normalized:
            raise serializers.ValidationError("Telefone inválido. Use formato: (DDD) XXXX-XXXX ou (DDD) 9 XXXX-XXXX")
        return normalized

    def validate_celular(self, value):
        """Valida CELULAR - obrigatório ter o 9º dígito"""
        if not value:
            return value
        normalized = normalize_phone_brazil(value)
        if not normalized:
            raise serializers.ValidationError("Celular inválido. Use formato: (DDD) 9 XXXX-XXXX")
        return normalized
    
    def _get_redes_sociais_data(self):
        """Extrai redes sociais do request"""
        import json
        request = self.context.get('request')
        if not request:
            return None
        
        redes_data = request.data.get('redes_sociais_input')
        if redes_data is None:
            return None
        
        # Se vier como string JSON, converter para lista
        if isinstance(redes_data, str):
            try:
                redes_data = json.loads(redes_data)
            except (json.JSONDecodeError, TypeError):
                return []
        
        return redes_data if isinstance(redes_data, list) else []
    
    def _salvar_redes_sociais(self, contato, redes_sociais_data):
        """Salva as redes sociais do contato"""
        # Remove todas as existentes e recria
        contato.redes_sociais.all().delete()
        for rede in redes_sociais_data:
            if rede.get('tipo') and rede.get('valor'):
                ContatoRedeSocial.objects.create(
                    contato=contato,
                    tipo_id=rede['tipo'],
                    valor=rede['valor']
                )
    
    def create(self, validated_data):
        validated_data['proprietario'] = self.context['request'].user
        contato = super().create(validated_data)
        
        # Processar redes sociais do request
        redes_sociais_data = self._get_redes_sociais_data()
        if redes_sociais_data:
            self._salvar_redes_sociais(contato, redes_sociais_data)
        
        return contato
    
    def update(self, instance, validated_data):
        contato = super().update(instance, validated_data)
        
        # Processar redes sociais do request
        redes_sociais_data = self._get_redes_sociais_data()
        if redes_sociais_data is not None:
            self._salvar_redes_sociais(contato, redes_sociais_data)
        
        return contato


class EstagioFunilSerializer(serializers.ModelSerializer):
    total_oportunidades = serializers.SerializerMethodField()
    
    class Meta:
        model = EstagioFunil
        fields = ['id', 'nome', 'tipo', 'cor', 'total_oportunidades']
    
    def get_total_oportunidades(self, obj):
        return obj.oportunidades.count() + obj.leads.count()


class FunilEstagioSerializer(serializers.ModelSerializer):
    """Serializa o vínculo entre Funil e Estágio, incluindo dados do estágio"""
    nome = serializers.CharField(source='estagio.nome', read_only=True)
    cor = serializers.CharField(source='estagio.cor', read_only=True)
    tipo = serializers.CharField(source='estagio.tipo', read_only=True)
    estagio_id = serializers.IntegerField(source='estagio.id')
    
    class Meta:
        model = FunilEstagio
        fields = ['id', 'estagio_id', 'nome', 'cor', 'tipo', 'ordem', 'is_padrao']


class FunilSerializer(serializers.ModelSerializer):
    estagios_detalhe = FunilEstagioSerializer(source='funilestagio_set', many=True, read_only=True)
    
    class Meta:
        model = Funil
        fields = ['id', 'nome', 'tipo', 'usuarios', 'is_active', 'estagios_detalhe']
    
    def update(self, instance, validated_data):
        # Lógica para atualizar estágios se enviados (opcional, faremos via ação dedicada se preferir)
        return super().update(instance, validated_data)


class PlanoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plano
        fields = '__all__'


class PlanoAdicionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanoAdicional
        fields = '__all__'


class OportunidadeAdicionalSerializer(serializers.ModelSerializer):
    adicional_nome = serializers.CharField(source='adicional.nome', read_only=True)
    adicional_preco = serializers.DecimalField(source='adicional.preco', max_digits=10, decimal_places=2, read_only=True)
    adicional_unidade = serializers.CharField(source='adicional.unidade', read_only=True)

    class Meta:
        model = OportunidadeAdicional
        fields = ['id', 'adicional', 'adicional_nome', 'adicional_preco', 'adicional_unidade', 'quantidade']


class OportunidadeSerializer(serializers.ModelSerializer):
    proprietario_nome = serializers.SerializerMethodField()
    proprietario = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    conta_nome = serializers.SerializerMethodField()
    contato_nome = serializers.SerializerMethodField()
    estagio_nome = serializers.SerializerMethodField()
    estagio_cor = serializers.SerializerMethodField()
    estagio_tipo = serializers.SerializerMethodField()
    plano_nome = serializers.SerializerMethodField()
    indicador_nome = serializers.SerializerMethodField()
    canal_nome = serializers.SerializerMethodField()
    contato_telefone = serializers.SerializerMethodField()
    whatsapp_nao_lidas = serializers.SerializerMethodField()
    adicionais_detalhes = OportunidadeAdicionalSerializer(source='oportunidadeadicional_set', many=True, read_only=True)
    
    class Meta:
        model = Oportunidade
        fields = [
            'id', 'nome', 'valor_estimado', 'data_fechamento_esperada',
            'probabilidade', 'funil', 'estagio', 'estagio_nome', 'estagio_cor', 'estagio_tipo',
            'conta', 'conta_nome', 'contato_principal', 'contato_nome',
            'proprietario', 'proprietario_nome', 'descricao', 'motivo_perda',
            'data_fechamento_real', 'plano', 'plano_nome', 'periodo_pagamento',
            'adicionais_detalhes', 'cortesia', 
            'cupom_desconto', 'forma_pagamento', 'indicador_comissao', 'indicador_nome', 
            'canal', 'canal_nome', 'contato_telefone', 'whatsapp_nao_lidas', 'data_criacao', 'data_atualizacao'
        ]
        read_only_fields = ['data_criacao', 'data_atualizacao', 'proprietario', 'whatsapp_nao_lidas']
    
    def get_whatsapp_nao_lidas(self, obj):
        return obj.mensagens_whatsapp.filter(lida=False, de_mim=False).count()
    
    def get_proprietario_nome(self, obj):
        return obj.proprietario.get_full_name() if obj.proprietario else "N/A"

    def get_conta_nome(self, obj):
        return obj.conta.nome_empresa if obj.conta else "N/A"

    def get_estagio_nome(self, obj):
        return obj.estagio.nome if obj.estagio else "N/A"

    def get_estagio_cor(self, obj):
        return obj.estagio.cor if obj.estagio else "#3B82F6"

    def get_estagio_tipo(self, obj):
        return obj.estagio.tipo if obj.estagio else "ABERTO"

    def get_contato_nome(self, obj):
        return obj.contato_principal.nome if obj.contato_principal else None

    def get_contato_telefone(self, obj):
        return obj.contato_principal.telefone if obj.contato_principal else None

    def get_plano_nome(self, obj):
        return obj.plano.nome if obj.plano else None
    
    def get_indicador_nome(self, obj):
        return obj.indicador_comissao.nome if obj.indicador_comissao else "Direto"

    def get_canal_nome(self, obj):
        return obj.canal.nome if obj.canal else "N/A"

    def create(self, validated_data):
        adicionais_data = self.context['request'].data.get('adicionais_itens', [])
        validated_data['proprietario'] = self.context['request'].user
        
        try:
            with transaction.atomic():
                # Removemos campos que podem ter vindo no validated_data mas são read-only no banco (como ID se enviado por engano)
                validated_data.pop('id', None)
                
                # Truncamos campos de texto para segurança
                if 'nome' in validated_data:
                    validated_data['nome'] = validated_data['nome'][:255]
                
                oportunidade = Oportunidade.objects.create(**validated_data)
                
                for item in adicionais_data:
                    if item.get('adicional'):
                        OportunidadeAdicional.objects.create(
                            oportunidade=oportunidade,
                            adicional_id=item['adicional'],
                            quantidade=item.get('quantidade', 1)
                        )
                return oportunidade
        except Exception as e:
            raise serializers.ValidationError(str(e))

    def update(self, instance, validated_data):
        adicionais_data = self.context['request'].data.get('adicionais_itens')
        
        try:
            with transaction.atomic():
                # Atualização manual para evitar AssertionError do DRF com campos read-only
                for attr, value in validated_data.items():
                    if attr == 'nome' and value:
                        value = value[:255]
                    setattr(instance, attr, value)
                instance.save()
                
                # Se os adicionais foram enviados, atualiza-os (substitui tudo)
                if adicionais_data is not None:
                    instance.oportunidadeadicional_set.all().delete()
                    for item in adicionais_data:
                        if item.get('adicional'):
                            OportunidadeAdicional.objects.create(
                                oportunidade=instance,
                                adicional_id=item['adicional'],
                                quantidade=item.get('quantidade', 1)
                            )
                return instance
        except Exception as e:
            raise serializers.ValidationError(str(e))


class OportunidadeKanbanSerializer(serializers.ModelSerializer):
    conta_nome = serializers.SerializerMethodField()
    contato_nome = serializers.SerializerMethodField()
    proprietario_nome = serializers.SerializerMethodField()
    estagio_id = serializers.SerializerMethodField()
    contato_telefone = serializers.SerializerMethodField()
    whatsapp_nao_lidas = serializers.SerializerMethodField()
    adicionais_detalhes = OportunidadeAdicionalSerializer(source='oportunidadeadicional_set', many=True, read_only=True)

    def get_conta_nome(self, obj):
        return obj.conta.nome_empresa if obj.conta else "N/A"

    def get_whatsapp_nao_lidas(self, obj):
        return obj.mensagens_whatsapp.filter(lida=False, de_mim=False).count()

    def get_contato_nome(self, obj):
        return obj.contato_principal.nome if obj.contato_principal else None

    def get_contato_telefone(self, obj):
        return obj.contato_principal.telefone if obj.contato_principal else None

    def get_proprietario_nome(self, obj):
        return obj.proprietario.get_full_name() if obj.proprietario else "N/A"
    
    def get_estagio_id(self, obj):
        return obj.estagio.id if obj.estagio else None
    
    class Meta:
        model = Oportunidade
        fields = [
            'id', 'nome', 'valor_estimado', 'data_fechamento_esperada',
            'probabilidade', 'estagio', 'estagio_id', 'conta', 'conta_nome', 'contato_principal', 'contato_nome', 'contato_telefone',
            'proprietario_nome', 'plano', 'periodo_pagamento', 'indicador_comissao', 'canal', 'whatsapp_nao_lidas', 'adicionais_detalhes'
        ]


class AtividadeSerializer(serializers.ModelSerializer):
    proprietario_nome = serializers.CharField(source='proprietario.get_full_name', read_only=True)
    
    class Meta:
        model = Atividade
        fields = [
            'id', 'tipo', 'titulo', 'descricao', 'data_vencimento',
            'status', 'content_type', 'object_id',
            'proprietario', 'proprietario_nome',
            'data_criacao', 'data_atualizacao', 'data_conclusao'
        ]
        read_only_fields = ['data_criacao', 'data_atualizacao', 'proprietario']
    
    def create(self, validated_data):
        if 'proprietario' not in validated_data:
            validated_data['proprietario'] = self.context['request'].user
        return super().create(validated_data)


class LeadConversaoSerializer(serializers.Serializer):
    criar_oportunidade = serializers.BooleanField(default=False)
    nome_oportunidade = serializers.CharField(required=False, allow_blank=True)
    valor_estimado = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        allow_null=True
    )
    canal = serializers.IntegerField(required=False, allow_null=True)


class WhatsappMessageSerializer(serializers.ModelSerializer):
    contato = serializers.SerializerMethodField()

    def get_contato(self, obj):
        """Retorna o número do contato (o que não é a instância/de_mim)"""
        # Se fui eu que mandei, o contato é o destinatário
        # Se recebi, o contato é o remetente
        if obj.de_mim:
            return obj.numero_destinatario
        return obj.numero_remetente

    class Meta:
        model = WhatsappMessage
        fields = '__all__'
