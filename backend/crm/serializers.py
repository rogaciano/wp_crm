"""
Serializers para a API do CRM
"""
from rest_framework import serializers
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
    proprietario = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    diagnosticos = DiagnosticoResultadoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Lead
        fields = [
            'id', 'nome', 'email', 'telefone', 'empresa', 'cargo',
            'fonte', 'status', 'notas', 'proprietario', 'proprietario_nome',
            'diagnosticos', 'data_criacao', 'data_atualizacao'
        ]
        read_only_fields = ['data_criacao', 'data_atualizacao', 'proprietario', 'diagnosticos']
    
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
    proprietario_nome = serializers.CharField(source='proprietario.get_full_name', read_only=True)
    proprietario = serializers.PrimaryKeyRelatedField(read_only=True, required=False)
    conta_nome = serializers.CharField(source='conta.nome_empresa', read_only=True)
    contato_nome = serializers.SerializerMethodField()
    estagio_nome = serializers.CharField(source='estagio.nome', read_only=True)
    estagio_cor = serializers.CharField(source='estagio.cor', read_only=True)
    estagio_tipo = serializers.CharField(source='estagio.tipo', read_only=True)
    plano_nome = serializers.SerializerMethodField()
    indicador_nome = serializers.SerializerMethodField()
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
            'cupom_desconto', 'forma_pagamento', 'indicador_comissao', 
            'suporte_regiao', 'data_criacao', 'data_atualizacao'
        ]
        read_only_fields = ['data_criacao', 'data_atualizacao', 'proprietario']
    
    def get_contato_nome(self, obj):
        return obj.contato_principal.nome if obj.contato_principal else None

    def get_plano_nome(self, obj):
        return obj.plano.nome if obj.plano else None
    
    def get_indicador_nome(self, obj):
        return obj.indicador_comissao.nome if obj.indicador_comissao else None

    def create(self, validated_data):
        adicionais_data = self.context['request'].data.get('adicionais_itens', [])
        validated_data['proprietario'] = self.context['request'].user
        oportunidade = Oportunidade.objects.create(**validated_data)
        
        for item in adicionais_data:
            OportunidadeAdicional.objects.create(
                oportunidade=oportunidade,
                adicional_id=item['adicional'],
                quantidade=item.get('quantidade', 1)
            )
            
        return oportunidade

    def update(self, instance, validated_data):
        adicionais_data = self.context['request'].data.get('adicionais_itens')
        
        # Atualiza campos básicos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Se os adicionais foram enviados, atualiza-os (substitui tudo)
        if adicionais_data is not None:
            instance.oportunidadeadicional_set.all().delete()
            for item in adicionais_data:
                OportunidadeAdicional.objects.create(
                    oportunidade=instance,
                    adicional_id=item['adicional'],
                    quantidade=item.get('quantidade', 1)
                )
                
        return instance


class OportunidadeKanbanSerializer(serializers.ModelSerializer):
    conta_nome = serializers.CharField(source='conta.nome_empresa', read_only=True)
    contato_nome = serializers.SerializerMethodField()
    proprietario_nome = serializers.CharField(source='proprietario.get_full_name', read_only=True)

    def get_contato_nome(self, obj):
        return obj.contato_principal.nome if obj.contato_principal else None
    
    class Meta:
        model = Oportunidade
        fields = [
            'id', 'nome', 'valor_estimado', 'data_fechamento_esperada',
            'probabilidade', 'estagio', 'conta_nome', 'contato_nome',
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
