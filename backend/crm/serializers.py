"""
Serializers para a API do CRM
"""
from rest_framework import serializers
from django.db import transaction
from django.contrib.auth.password_validation import validate_password
from .models import (
    Canal, User, Lead, Conta, Contato, EstagioFunil, Oportunidade, Atividade,
    DiagnosticoPilar, DiagnosticoPergunta, DiagnosticoResposta, DiagnosticoResultado, 
    Plano, PlanoAdicional, OportunidadeAdicional
)


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
    
    def get_canal_nome(self, obj):
        return obj.canal.nome if obj.canal else "N/A"
        
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'perfil', 'canal', 'canal_nome', 'telefone',
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
    
    class Meta:
        model = Lead
        fields = [
            'id', 'nome', 'email', 'telefone', 'empresa', 'cargo',
            'fonte', 'status', 'notas', 'proprietario', 'proprietario_nome', 'proprietario_canal',
            'diagnosticos', 'data_criacao', 'data_atualizacao'
        ]
        read_only_fields = ['data_criacao', 'data_atualizacao', 'proprietario', 'diagnosticos']
    
    def get_proprietario_canal(self, obj):
        return obj.proprietario.canal.id if obj.proprietario and obj.proprietario.canal else None

    def create(self, validated_data):
        # Define o proprietário como o usuário logado
        if 'request' in self.context and self.context['request'].user.is_authenticated:
            validated_data['proprietario'] = self.context['request'].user
        return super().create(validated_data)


class ContaSerializer(serializers.ModelSerializer):
    proprietario_nome = serializers.CharField(source='proprietario.get_full_name', read_only=True)
    proprietario = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    total_contatos = serializers.SerializerMethodField()
    total_oportunidades = serializers.SerializerMethodField()
    diagnosticos = DiagnosticoResultadoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conta
        fields = [
            'id', 'nome_empresa', 'cnpj', 'telefone_principal', 'email',
            'website', 'setor', 'endereco', 'cidade', 'estado', 'cep',
            'notas', 'proprietario', 'proprietario_nome',
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


class ContatoSerializer(serializers.ModelSerializer):
    proprietario_nome = serializers.CharField(source='proprietario.get_full_name', read_only=True)
    proprietario = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    conta_nome = serializers.CharField(source='conta.nome_empresa', read_only=True)
    
    class Meta:
        model = Contato
        fields = [
            'id', 'nome', 'email', 'telefone', 'celular', 'cargo',
            'departamento', 'tipo', 'conta', 'conta_nome', 'proprietario',
            'proprietario_nome', 'notas',
            'data_criacao', 'data_atualizacao'
        ]
        read_only_fields = ['data_criacao', 'data_atualizacao', 'proprietario']
    
    def create(self, validated_data):
        validated_data['proprietario'] = self.context['request'].user
        return super().create(validated_data)


class EstagioFunilSerializer(serializers.ModelSerializer):
    total_oportunidades = serializers.SerializerMethodField()
    
    class Meta:
        model = EstagioFunil
        fields = ['id', 'nome', 'ordem', 'tipo', 'cor', 'total_oportunidades']
    
    def get_total_oportunidades(self, obj):
        return obj.oportunidades.count()


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
    adicionais_detalhes = OportunidadeAdicionalSerializer(source='oportunidadeadicional_set', many=True, read_only=True)
    
    class Meta:
        model = Oportunidade
        fields = [
            'id', 'nome', 'valor_estimado', 'data_fechamento_esperada',
            'probabilidade', 'estagio', 'estagio_nome', 'estagio_cor', 'estagio_tipo',
            'conta', 'conta_nome', 'contato_principal', 'contato_nome',
            'proprietario', 'proprietario_nome', 'descricao', 'motivo_perda',
            'data_fechamento_real', 'plano', 'plano_nome', 'periodo_pagamento',
            'adicionais_detalhes', 'cortesia', 
            'cupom_desconto', 'forma_pagamento', 'indicador_comissao', 'indicador_nome', 
            'canal', 'canal_nome', 'data_criacao', 'data_atualizacao'
        ]
        read_only_fields = ['data_criacao', 'data_atualizacao', 'proprietario']
    
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

    def get_conta_nome(self, obj):
        return obj.conta.nome_empresa if obj.conta else "N/A"

    def get_contato_nome(self, obj):
        return obj.contato_principal.nome if obj.contato_principal else None

    def get_proprietario_nome(self, obj):
        return obj.proprietario.get_full_name() if obj.proprietario else "N/A"
    
    def get_estagio_id(self, obj):
        return obj.estagio.id if obj.estagio else None
    
    class Meta:
        model = Oportunidade
        fields = [
            'id', 'nome', 'valor_estimado', 'data_fechamento_esperada',
            'probabilidade', 'estagio', 'estagio_id', 'conta_nome', 'contato_nome',
            'proprietario_nome'
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
