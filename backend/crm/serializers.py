"""
Serializers para a API do CRM
"""
import re
from rest_framework import serializers
from django.db import transaction
from django.contrib.auth.password_validation import validate_password
from .models import (
    Canal, User, Conta, Contato, TipoContato, TipoRedeSocial, ContatoRedeSocial,
    Funil, EstagioFunil, FunilEstagio, Oportunidade, Atividade, Origem,
    DiagnosticoPilar, DiagnosticoPergunta, DiagnosticoResposta, DiagnosticoResultado,
    Plano, PlanoAdicional, OportunidadeAdicional, OportunidadeAnexo, WhatsappMessage, Log
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
    funil_padrao_nome = serializers.SerializerMethodField()
    estagio_inicial_nome = serializers.SerializerMethodField()
    
    def get_responsavel_nome(self, obj):
        return obj.responsavel.get_full_name() if obj.responsavel else "N/A"
    
    def get_funil_padrao_nome(self, obj):
        return obj.funil_padrao.nome if obj.funil_padrao else None
    
    def get_estagio_inicial_nome(self, obj):
        return obj.estagio_inicial.nome if obj.estagio_inicial else None
    
    class Meta:
        model = Canal
        fields = [
            'id', 'nome', 'slug', 'responsavel', 'responsavel_nome', 'total_vendedores',
            'funil_padrao', 'funil_padrao_nome', 'estagio_inicial', 'estagio_inicial_nome',
            'evolution_instance_name', 'evolution_is_connected', 'evolution_last_status',
            'evolution_phone_number', 'data_criacao'
        ]
        read_only_fields = [
            'data_criacao', 'evolution_is_connected', 'evolution_last_status',
            'evolution_phone_number'
        ]
    
    def get_total_vendedores(self, obj):
        return obj.vendedores.count()


class OrigemSerializer(serializers.ModelSerializer):
    """Serializer para Origem (Fonte de Oportunidades)"""
    class Meta:
        model = Origem
        fields = ['id', 'nome', 'ativo', 'data_criacao']
        read_only_fields = ['data_criacao']


class UserSerializer(serializers.ModelSerializer):
    canal_nome = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    funis_acesso = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    
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
            'password', 'is_active', 'date_joined', 'funis_acesso'
        ]
        read_only_fields = ['date_joined', 'funis_acesso']
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
    conta_nome = serializers.CharField(source='conta.nome_empresa', read_only=True)
    oportunidade_nome = serializers.CharField(source='oportunidade.nome', read_only=True)
    
    class Meta:
        model = DiagnosticoResultado
        fields = [
            'id', 'conta', 'conta_nome', 
            'oportunidade', 'oportunidade_nome', 'data_conclusao',
            'respostas_detalhadas', 'pontuacao_por_pilar', 'analise_ia'
        ]
        read_only_fields = ['data_conclusao']


class DiagnosticoPublicSubmissionSerializer(serializers.Serializer):
    """Serializer para submissão pública do diagnóstico e criação de Lead"""
    nome = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    telefone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    empresa = serializers.CharField(max_length=255, required=False, allow_blank=True)
    
    # Novos campos para vincular a entidades existentes
    contato_id = serializers.IntegerField(required=False, allow_null=True)
    oportunidade_id = serializers.IntegerField(required=False, allow_null=True)
    
    # Lista de IDs das respostas escolhidas
    respostas_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )





class ContaMarcaSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import ContaMarca
        model = ContaMarca
        fields = ['id', 'nome']


class ContaSerializer(serializers.ModelSerializer):
    proprietario_nome = serializers.CharField(source='proprietario.get_full_name', read_only=True)
    proprietario = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    total_contatos = serializers.SerializerMethodField()
    total_oportunidades = serializers.SerializerMethodField()
    diagnosticos = DiagnosticoResultadoSerializer(many=True, read_only=True)
    marcas_adicionais = ContaMarcaSerializer(many=True, read_only=True)
    status_cliente_display = serializers.CharField(source='get_status_cliente_display', read_only=True)
    
    canal_nome = serializers.CharField(source='canal.nome', read_only=True)
    
    class Meta:
        model = Conta
        fields = [
            'id', 'nome_empresa', 'marca', 'marcas_adicionais', 'cnpj', 'telefone_principal', 'email',
            'website', 'setor', 'endereco', 'cidade', 'estado', 'cep',
            'status_cliente', 'status_cliente_display', 'data_ativacao_cliente',
            'notas', 'canal', 'canal_nome', 'proprietario', 'proprietario_nome',
            'total_contatos', 'total_oportunidades', 'diagnosticos',
            'data_criacao', 'data_atualizacao'
        ]
        read_only_fields = ['data_criacao', 'data_atualizacao', 'proprietario', 'diagnosticos', 'marcas_adicionais']
    
    def get_total_contatos(self, obj):
        return obj.contatos.count()
    
    def get_total_oportunidades(self, obj):
        from django.db.models import Q
        from .models import Oportunidade
        return Oportunidade.objects.filter(Q(conta=obj) | Q(empresas=obj)).distinct().count()
    
    def _salvar_marcas_adicionais(self, conta, marcas_data):
        """Salva as marcas adicionais da conta"""
        import json
        from .models import ContaMarca
        
        if not marcas_data:
            return

        # Se vier string JSON, converte
        if isinstance(marcas_data, str):
            try:
                marcas_data = json.loads(marcas_data)
            except (json.JSONDecodeError, TypeError):
                marcas_data = []
        
        if not isinstance(marcas_data, list):
            return

        # Limpa e recria (estratégia simples)
        conta.marcas_adicionais.all().delete()
        for marca in marcas_data:
            if isinstance(marca, dict):
                nome = marca.get('nome')
            else:
                nome = str(marca)
                
            if nome and nome.strip():
                ContaMarca.objects.create(conta=conta, nome=nome.strip())

    def create(self, validated_data):
        validated_data['proprietario'] = self.context['request'].user
        conta = super().create(validated_data)
        
        # Processar marcas adicionais
        marcas_input = self.context['request'].data.get('marcas_adicionais_input')
        if marcas_input:
            self._salvar_marcas_adicionais(conta, marcas_input)
            
        return conta

    def update(self, instance, validated_data):
        conta = super().update(instance, validated_data)
        
        # Processar marcas adicionais
        marcas_input = self.context['request'].data.get('marcas_adicionais_input')
        if marcas_input is not None:
            self._salvar_marcas_adicionais(conta, marcas_input)
            
        return conta



class TipoContatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoContato
        fields = ['id', 'nome', 'emoji', 'descricao', 'data_criacao']


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


class ContatoTelefoneSerializer(serializers.ModelSerializer):
    """Serializer para múltiplos telefones"""
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        from .models import ContatoTelefone
        model = ContatoTelefone
        fields = ['id', 'numero', 'tipo', 'tipo_display', 'principal']


class ContatoEmailSerializer(serializers.ModelSerializer):
    """Serializer para múltiplos emails"""
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        from .models import ContatoEmail
        model = ContatoEmail
        fields = ['id', 'email', 'tipo', 'tipo_display', 'principal']


class TagSerializer(serializers.ModelSerializer):
    """Serializer para Tags"""
    class Meta:
        from .models import Tag
        model = Tag
        fields = ['id', 'nome', 'cor']


class ContatoAnexoSerializer(serializers.ModelSerializer):
    """Serializer para anexos de contatos"""
    uploaded_por_nome = serializers.CharField(source='uploaded_por.get_full_name', read_only=True)
    arquivo_url = serializers.SerializerMethodField()
    
    class Meta:
        from .models import ContatoAnexo
        model = ContatoAnexo
        fields = ['id', 'arquivo', 'arquivo_url', 'nome', 'descricao', 'data_upload', 'uploaded_por', 'uploaded_por_nome']
        read_only_fields = ['data_upload', 'uploaded_por']
    
    def get_arquivo_url(self, obj):
        if obj.arquivo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.arquivo.url)
            return obj.arquivo.url
        return None


class ContatoSerializer(serializers.ModelSerializer):
    proprietario_nome = serializers.CharField(source='proprietario.get_full_name', read_only=True)
    proprietario = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    conta_nome = serializers.CharField(source='conta.nome_empresa', read_only=True)
    tipo_contato_nome = serializers.CharField(source='tipo_contato.nome', read_only=True)
    tipo_contato_emoji = serializers.CharField(source='tipo_contato.emoji', read_only=True)
    canal_nome = serializers.CharField(source='canal.nome', read_only=True)
    telefone_formatado = serializers.SerializerMethodField()
    celular_formatado = serializers.SerializerMethodField()
    foto_url = serializers.SerializerMethodField()
    redes_sociais = ContatoRedeSocialSerializer(many=True, read_only=True)
    
    # Novos campos para múltiplos telefones/emails
    telefones = ContatoTelefoneSerializer(many=True, read_only=True)
    emails = ContatoEmailSerializer(many=True, read_only=True)
    tags_detail = TagSerializer(source='tags', many=True, read_only=True)
    anexos = ContatoAnexoSerializer(many=True, read_only=True)
    oportunidades = serializers.SerializerMethodField()

    # Campos de auditoria
    criado_por_nome = serializers.CharField(source='criado_por.get_full_name', read_only=True)
    atualizado_por_nome = serializers.CharField(source='atualizado_por.get_full_name', read_only=True)

    class Meta:
        model = Contato
        fields = [
            'id', 'nome', 'email', 'telefone', 'telefone_formatado', 'celular', 'celular_formatado', 'cargo',
            'departamento', 'chave_pix', 'foto', 'foto_url', 'tipo_contato', 'tipo_contato_nome', 'tipo_contato_emoji', 'tipo',
            'conta', 'conta_nome', 'canal', 'canal_nome',
            'proprietario', 'proprietario_nome', 'notas',
            'redes_sociais', 'telefones', 'emails', 'tags', 'tags_detail', 'anexos', 'oportunidades',
            'data_criacao', 'data_atualizacao',
            'criado_por', 'criado_por_nome', 'atualizado_por', 'atualizado_por_nome'
        ]
        read_only_fields = [
            'data_criacao', 'data_atualizacao', 'proprietario', 'telefone_formatado', 'celular_formatado',
            'foto_url', 'redes_sociais', 'tipo_contato_emoji', 'criado_por', 'atualizado_por',
            'criado_por_nome', 'atualizado_por_nome'
        ]
    
    def get_foto_url(self, obj):
        if obj.foto:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.foto.url)
            return obj.foto.url
        return None
    
    def get_telefone_formatado(self, obj):
        phone = obj.telefone
        if not phone:
            tel = obj.telefones.filter(principal=True).first() or obj.telefones.first()
            if tel:
                phone = tel.numero
        return format_phone_display(phone) if phone else ''
    
    def get_celular_formatado(self, obj):
        phone = obj.celular
        if not phone:
            tel = obj.telefones.filter(principal=True).first() or obj.telefones.first()
            if tel:
                phone = tel.numero
        return format_phone_display(phone) if phone else ''
    
    def get_oportunidades(self, obj):
        """Retorna as oportunidades vinculadas a este contato"""
        from django.db.models import Q
        from .models import Oportunidade
        opps = Oportunidade.objects.filter(Q(contato_principal=obj) | Q(contatos=obj)).distinct()
        return [{
            'id': opp.id,
            'nome': opp.nome,
            'valor_estimado': opp.valor_estimado,
            'estagio_nome': opp.estagio.nome,
            'estagio_cor': opp.estagio.cor,
            'data_atualizacao': opp.data_atualizacao
        } for opp in opps]
    
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
    
    def _get_telefones_data(self):
        """Extrai telefones do request"""
        import json
        request = self.context.get('request')
        if not request:
            return None
        
        data = request.data.get('telefones_input')
        if data is None:
            return None
        
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return []
        
        return data if isinstance(data, list) else []
    
    def _salvar_telefones(self, contato, telefones_data):
        """Salva os telefones do contato"""
        from .models import ContatoTelefone
        contato.telefones.all().delete()
        for tel in telefones_data:
            if tel.get('numero'):
                ContatoTelefone.objects.create(
                    contato=contato,
                    numero=tel['numero'],
                    tipo=tel.get('tipo', 'CELULAR'),
                    principal=tel.get('principal', False)
                )
    
    def _get_emails_data(self):
        """Extrai emails do request"""
        import json
        request = self.context.get('request')
        if not request:
            return None
        
        data = request.data.get('emails_input')
        if data is None:
            return None
        
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return []
        
        return data if isinstance(data, list) else []
    
    def _salvar_emails(self, contato, emails_data):
        """Salva os emails do contato"""
        from .models import ContatoEmail
        contato.emails.all().delete()
        for email in emails_data:
            if email.get('email'):
                ContatoEmail.objects.create(
                    contato=contato,
                    email=email['email'],
                    tipo=email.get('tipo', 'COMERCIAL'),
                    principal=email.get('principal', False)
                )
    
    def _get_tags_data(self):
        """Extrai tags do request"""
        import json
        request = self.context.get('request')
        if not request:
            return None
        
        data = request.data.get('tags_input')
        if data is None:
            return None
        
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except (json.JSONDecodeError, TypeError):
                return []
        
        return data if isinstance(data, list) else []
    
    def _salvar_tags(self, contato, tags_data):
        """Salva as tags do contato"""
        from .models import Tag
        contato.tags.clear()
        for tag_id in tags_data:
            try:
                tag = Tag.objects.get(id=tag_id)
                contato.tags.add(tag)
            except Tag.DoesNotExist:
                pass

    def validate(self, data):
        """
        Valida unicidade dos telefones.
        Verifica se algum telefone (legado ou novo) já existe em OUTRO contato.
        """
        from .models import Contato, ContatoTelefone
        from django.db.models import Q
        
        # Coletar todos os telefones sendo salvos
        phones_to_check = set()
        
        # 1. Campos legado
        if data.get('telefone'):
            normalized = normalize_landline_brazil(data['telefone'])
            if normalized: phones_to_check.add(normalized)
            
        if data.get('celular'):
            normalized = normalize_phone_brazil(data['celular'])
            if normalized: phones_to_check.add(normalized)
            
        # 2. Novos campos (lista)
        telefones_input = self._get_telefones_data()
        if telefones_input:
            for item in telefones_input:
                num = item.get('numero')
                tipo = item.get('tipo', 'CELULAR')
                if num:
                    normalized = None
                    if tipo == 'CELULAR' or tipo == 'WHATSAPP':
                         normalized = normalize_phone_brazil(num)
                    else:
                         normalized = normalize_landline_brazil(num)
                    
                    if normalized:
                        phones_to_check.add(normalized)
        
        # Se não tiver telefones, ok (já validado se obrigatório no frontend/model)
        if not phones_to_check:
            return data
            
        # Verificar duplicidade no banco
        # Excluir o próprio contato se for edição
        exclude_id = self.instance.id if self.instance else None
        
        for phone in phones_to_check:
            # Busca em Contato (campos diretos legacy)
            qs_legacy = Contato.objects.filter(
                Q(telefone=phone) | Q(celular=phone)
            )
            if exclude_id:
                qs_legacy = qs_legacy.exclude(id=exclude_id)
            
            existing_legacy = qs_legacy.first()
            
            if existing_legacy:
                canal_nome = existing_legacy.canal.nome if existing_legacy.canal else "Sem Canal"
                raise serializers.ValidationError(
                    f"O telefone {format_phone_display(phone)} já pertence ao contato '{existing_legacy.nome}' "
                    f"no canal '{canal_nome}'. Não é permitido contatos duplicados."
                )
                
            # Busca em ContatoTelefone (nova tabela)
            qs_new = ContatoTelefone.objects.filter(numero=phone)
            if exclude_id:
                qs_new = qs_new.exclude(contato_id=exclude_id)
                
            existing_new = qs_new.first()
            
            if existing_new:
                contato_dono = existing_new.contato
                canal_nome = contato_dono.canal.nome if contato_dono.canal else "Sem Canal"
                raise serializers.ValidationError(
                    f"O telefone {format_phone_display(phone)} já pertence ao contato '{contato_dono.nome}' "
                    f"no canal '{canal_nome}'. Não é permitido contatos duplicados."
                )

        # ==============================================================================
        # Validação de Emails Duplicados
        # ==============================================================================
        from .models import ContatoEmail
        
        emails_to_check = set()
        
        # 1. Campo legado
        if data.get('email'):
            emails_to_check.add(data['email'].strip().lower())
            
        # 2. Novos campos (lista)
        emails_input = self._get_emails_data()
        if emails_input:
            for item in emails_input:
                email = item.get('email')
                if email:
                    emails_to_check.add(email.strip().lower())
                    
        for email in emails_to_check:
            # Busca em Contato (campo direto legacy)
            qs_legacy = Contato.objects.filter(email=email)
            if exclude_id:
                qs_legacy = qs_legacy.exclude(id=exclude_id)
                
            existing_legacy = qs_legacy.first()
            
            if existing_legacy:
                canal_nome = existing_legacy.canal.nome if existing_legacy.canal else "Sem Canal"
                raise serializers.ValidationError(
                    f"O e-mail {email} já pertence ao contato '{existing_legacy.nome}' "
                    f"no canal '{canal_nome}'. Não é permitido contatos duplicados."
                )
            
            # Busca em ContatoEmail (nova tabela)
            qs_new = ContatoEmail.objects.filter(email=email)
            if exclude_id:
                qs_new = qs_new.exclude(contato_id=exclude_id)
                
            existing_new = qs_new.first()
            
            if existing_new:
                contato_dono = existing_new.contato
                canal_nome = contato_dono.canal.nome if contato_dono.canal else "Sem Canal"
                raise serializers.ValidationError(
                    f"O e-mail {email} já pertence ao contato '{contato_dono.nome}' "
                    f"no canal '{canal_nome}'. Não é permitido contatos duplicados."
                )

        return data
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['proprietario'] = user
        validated_data['criado_por'] = user
        validated_data['atualizado_por'] = user
        contato = super().create(validated_data)

        # Processar redes sociais do request
        redes_sociais_data = self._get_redes_sociais_data()
        if redes_sociais_data:
            self._salvar_redes_sociais(contato, redes_sociais_data)
        
        # Processar telefones
        telefones_data = self._get_telefones_data()
        if telefones_data:
            self._salvar_telefones(contato, telefones_data)
        
        # Processar emails
        emails_data = self._get_emails_data()
        if emails_data:
            self._salvar_emails(contato, emails_data)
        
        # Processar tags
        tags_data = self._get_tags_data()
        if tags_data:
            self._salvar_tags(contato, tags_data)

        return contato

    def update(self, instance, validated_data):
        user = self.context['request'].user
        validated_data['atualizado_por'] = user
        contato = super().update(instance, validated_data)

        # Processar redes sociais do request
        redes_sociais_data = self._get_redes_sociais_data()
        if redes_sociais_data is not None:
            self._salvar_redes_sociais(contato, redes_sociais_data)
        
        # Processar telefones
        telefones_data = self._get_telefones_data()
        if telefones_data is not None:
            self._salvar_telefones(contato, telefones_data)
        
        # Processar emails
        emails_data = self._get_emails_data()
        if emails_data is not None:
            self._salvar_emails(contato, emails_data)
        
        # Processar tags
        tags_data = self._get_tags_data()
        if tags_data is not None:
            self._salvar_tags(contato, tags_data)

        return contato


class EstagioFunilSerializer(serializers.ModelSerializer):
    total_oportunidades = serializers.SerializerMethodField()
    
    class Meta:
        model = EstagioFunil
        fields = ['id', 'nome', 'tipo', 'cor', 'total_oportunidades']
    
    def get_total_oportunidades(self, obj):
        return obj.oportunidades.count()


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

    def validate(self, data):
        tipo = data.get('tipo', getattr(self.instance, 'tipo', None))
        if tipo in ('POS_VENDA', 'SUPORTE'):
            qs = Funil.objects.filter(tipo=tipo)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    f"Já existe um funil do tipo {tipo}. Apenas 1 é permitido."
                )
        return data

    def update(self, instance, validated_data):
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


class OportunidadeAnexoSerializer(serializers.ModelSerializer):
    uploaded_por_nome = serializers.CharField(source='uploaded_por.get_full_name', read_only=True)
    
    class Meta:
        model = OportunidadeAnexo
        fields = ['id', 'oportunidade', 'arquivo', 'nome', 'descricao', 'data_upload', 'uploaded_por', 'uploaded_por_nome']
        read_only_fields = ['data_upload', 'uploaded_por']


class OportunidadeSerializer(serializers.ModelSerializer):
    proprietario_nome = serializers.CharField(source='proprietario.get_full_name', read_only=True)
    proprietario = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)
    conta_nome = serializers.SerializerMethodField()
    contato_nome = serializers.SerializerMethodField()
    estagio_nome = serializers.SerializerMethodField()
    estagio_cor = serializers.SerializerMethodField()
    estagio_tipo = serializers.SerializerMethodField()
    plano_nome = serializers.SerializerMethodField()
    indicador_nome = serializers.SerializerMethodField()
    origem_nome = serializers.SerializerMethodField()
    canal_nome = serializers.SerializerMethodField()
    funil_nome = serializers.SerializerMethodField()
    funil_tipo = serializers.SerializerMethodField()
    contato_telefone = serializers.SerializerMethodField()
    contato_celular = serializers.SerializerMethodField()
    whatsapp_nao_lidas = serializers.SerializerMethodField()
    adicionais_detalhes = OportunidadeAdicionalSerializer(source='oportunidadeadicional_set', many=True, read_only=True)
    anexos = OportunidadeAnexoSerializer(many=True, read_only=True)
    diagnosticos = DiagnosticoResultadoSerializer(many=True, read_only=True)
    proxima_atividade = serializers.SerializerMethodField()
    
    # Detalhes das relações M2M para leitura
    contatos_detalhe = ContatoSerializer(source='contatos', many=True, read_only=True)
    empresas_detalhe = ContaSerializer(source='empresas', many=True, read_only=True)
    
    # Dados completos para edição no frontend
    contato_principal_dados = ContatoSerializer(source='contato_principal', read_only=True)
    conta_dados = ContaSerializer(source='conta', read_only=True)
    
    class Meta:
        model = Oportunidade
        fields = [
            'id', 'nome', 'valor_estimado', 'data_fechamento_esperada',
            'probabilidade', 'funil', 'estagio', 'estagio_nome', 'estagio_cor', 'estagio_tipo',
            'conta', 'conta_nome', 'contato_principal', 'contato_nome',
            'proprietario', 'proprietario_nome', 'descricao', 'motivo_perda',
            'data_fechamento_real', 'plano', 'plano_nome', 'periodo_pagamento',
            'adicionais_detalhes', 'cortesia', 'anexos', 'diagnosticos',
            'cupom_desconto', 'forma_pagamento', 'indicador_comissao', 'indicador_nome', 
            'canal', 'canal_nome', 'funil_nome', 'funil_tipo', 'contato_telefone', 'contato_celular', 'whatsapp_nao_lidas', 'fonte', 'origem', 'origem_nome',
            'contatos', 'empresas', 'contatos_detalhe', 'empresas_detalhe',
            'contato_principal_dados', 'conta_dados',
            'data_criacao', 'data_atualizacao', 'proxima_atividade'
        ]
        read_only_fields = ['data_criacao', 'data_atualizacao', 'proprietario', 'whatsapp_nao_lidas']
        extra_kwargs = {
            'funil': {'required': False, 'allow_null': True},
            'estagio': {'required': False, 'allow_null': True},
        }
    
    def get_proxima_atividade(self, obj):
        from django.utils import timezone
        next_activity = obj.atividades.filter(
            status='PENDENTE', 
            data_vencimento__gte=timezone.now()
        ).order_by('data_vencimento').first()
        
        if next_activity:
            return {
                'id': next_activity.id,
                'titulo': next_activity.titulo,
                'data': next_activity.data_vencimento
            }
        return None
    
    def get_whatsapp_nao_lidas(self, obj):
        return obj.mensagens_whatsapp.filter(lida=False, de_mim=False).count()
    
    def get_conta_nome(self, obj):
        if obj.empresas.exists():
            return ", ".join([e.nome_empresa for e in obj.empresas.all()])
        return obj.conta.nome_empresa if obj.conta else None

    def get_estagio_nome(self, obj):
        return obj.estagio.nome if obj.estagio else "N/A"

    def get_estagio_cor(self, obj):
        return obj.estagio.cor if obj.estagio else "#3B82F6"

    def get_estagio_tipo(self, obj):
        return obj.estagio.tipo if obj.estagio else "ABERTO"

    def get_contato_nome(self, obj):
        if obj.contatos.exists():
            return ", ".join([c.nome for c in obj.contatos.all()])
        return obj.contato_principal.nome if obj.contato_principal else None

    def get_contato_telefone(self, obj):
        if not obj.contato_principal: return None
        c = obj.contato_principal
        phone = c.celular or c.telefone
        if not phone:
            tel = c.telefones.filter(principal=True).first() or c.telefones.first()
            if tel:
                phone = tel.numero
        return format_phone_display(phone) if phone else None

    def get_contato_celular(self, obj):
        if not obj.contato_principal: return None
        c = obj.contato_principal
        phone = c.celular or c.telefone
        if not phone:
            tel = c.telefones.filter(principal=True).first() or c.telefones.first()
            if tel:
                phone = tel.numero
        return format_phone_display(phone) if phone else None

    def get_plano_nome(self, obj):
        return obj.plano.nome if obj.plano else None
    
    def get_indicador_nome(self, obj):
        return obj.indicador_comissao.nome if obj.indicador_comissao else "Direto"

    def get_origem_nome(self, obj):
        return obj.origem.nome if obj.origem else (obj.fonte or "N/A")

    def get_canal_nome(self, obj):
        return obj.canal.nome if obj.canal else "N/A"

    def get_funil_nome(self, obj):
        return obj.funil.nome if obj.funil else "N/A"

    def get_funil_tipo(self, obj):
        return obj.funil.tipo if obj.funil else "VENDAS"

    def create(self, validated_data):
        adicionais_data = self.context['request'].data.get('adicionais_itens', [])
        contatos_data = validated_data.pop('contatos', [])
        empresas_data = validated_data.pop('empresas', [])
        
        validated_data['proprietario'] = self.context['request'].user
        
        try:
            with transaction.atomic():
                validated_data.pop('id', None)
                if 'nome' in validated_data:
                    validated_data['nome'] = validated_data['nome'][:255]
                
                oportunidade = Oportunidade.objects.create(**validated_data)
                
                if contatos_data:
                    oportunidade.contatos.set(contatos_data)
                if empresas_data:
                    oportunidade.empresas.set(empresas_data)
                
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
        contatos_data = validated_data.pop('contatos', None)
        empresas_data = validated_data.pop('empresas', None)
        
        try:
            with transaction.atomic():
                for attr, value in validated_data.items():
                    if attr == 'nome' and value:
                        value = value[:255]
                    setattr(instance, attr, value)
                instance.save()
                
                if contatos_data is not None:
                    instance.contatos.set(contatos_data)
                if empresas_data is not None:
                    instance.empresas.set(empresas_data)
                
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
    proprietario_nome = serializers.CharField(source='proprietario.get_full_name', read_only=True)
    estagio_id = serializers.IntegerField(source='estagio.id', read_only=True)
    contato_telefone = serializers.SerializerMethodField()
    whatsapp_nao_lidas = serializers.SerializerMethodField()
    adicionais_detalhes = OportunidadeAdicionalSerializer(source='oportunidadeadicional_set', many=True, read_only=True)

    class Meta:
        model = Oportunidade
        fields = [
            'id', 'nome', 'valor_estimado', 'contato_nome', 'conta_nome', 
            'proprietario_nome', 'estagio', 'estagio_id', 'funil', 'contato_telefone', 
            'whatsapp_nao_lidas', 'adicionais_detalhes', 'data_atualizacao'
        ]

    def get_conta_nome(self, obj):
        if obj.empresas.exists():
            return ", ".join([e.nome_empresa for e in obj.empresas.all()])
        return obj.conta.nome_empresa if obj.conta else "N/A"

    def get_whatsapp_nao_lidas(self, obj):
        return obj.mensagens_whatsapp.filter(lida=False, de_mim=False).count()

    def get_contato_nome(self, obj):
        if obj.contatos.exists():
            return ", ".join([c.nome for c in obj.contatos.all()])
        return obj.contato_principal.nome if obj.contato_principal else None

    def get_contato_telefone(self, obj):
        if not obj.contato_principal: return None
        c = obj.contato_principal
        phone = c.celular or c.telefone
        return format_phone_display(phone) if phone else None


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


class LogSerializer(serializers.ModelSerializer):
    """Serializer para logs de auditoria"""
    usuario_nome = serializers.CharField(source='usuario.get_full_name', read_only=True)
    acao_display = serializers.CharField(source='get_acao_display', read_only=True)

    class Meta:
        model = Log
        fields = [
            'id',
            'usuario',
            'usuario_nome',
            'acao',
            'acao_display',
            'modelo',
            'objeto_id',
            'objeto_repr',
            'alteracoes',
            'ip_address',
            'user_agent',
            'observacao',
            'timestamp'
        ]
        read_only_fields = ['id', 'timestamp', 'usuario_nome', 'acao_display']


class HistoricoEstagioSerializer(serializers.ModelSerializer):
    """Serializer para histórico de mudanças de estágio"""
    usuario_nome = serializers.SerializerMethodField()
    data_mudanca_formatada = serializers.SerializerMethodField()
    
    class Meta:
        from .models import HistoricoEstagio
        model = HistoricoEstagio
        fields = [
            'id',
            'tipo_objeto',
            'estagio_anterior',
            'estagio_novo',
            'nome_estagio_anterior',
            'nome_estagio_novo',
            'usuario',
            'usuario_nome',
            'data_mudanca',
            'data_mudanca_formatada',
            'observacao'
        ]
        read_only_fields = ['id', 'data_mudanca']
    
    def get_usuario_nome(self, obj):
        if obj.usuario:
            return obj.usuario.get_full_name() or obj.usuario.username
        return 'Sistema'
    
    def get_data_mudanca_formatada(self, obj):
        return obj.data_mudanca.strftime('%d/%m/%Y às %H:%M')
