"""
Configuração do Django Admin para CRM
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    Canal, User, Conta, Contato, TipoContato, Funil, EstagioFunil, FunilEstagio, Oportunidade, Atividade,
    DiagnosticoPilar, DiagnosticoPergunta, DiagnosticoResposta, DiagnosticoResultado,
    Plano, PlanoAdicional, Log
)


class FunilEstagioInline(admin.TabularInline):
    model = FunilEstagio
    extra = 1

@admin.register(Funil)
class FunilAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'is_active', 'data_criacao']
    list_filter = ['tipo', 'is_active']
    search_fields = ['nome']
    filter_horizontal = ['usuarios']
    inlines = [FunilEstagioInline]


@admin.register(Canal)
class CanalAdmin(admin.ModelAdmin):
    list_display = ['nome', 'responsavel', 'data_criacao']
    search_fields = ['nome']
    list_filter = ['data_criacao']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'perfil', 'canal', 'is_active']
    list_filter = ['perfil', 'canal', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informações CRM', {'fields': ('perfil', 'canal', 'telefone')}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informações CRM', {'fields': ('perfil', 'canal', 'telefone')}),
    )




@admin.register(Conta)
class ContaAdmin(admin.ModelAdmin):
    list_display = ['nome_empresa', 'cnpj', 'telefone_principal', 'cidade', 'proprietario', 'data_criacao']
    list_filter = ['setor', 'estado', 'data_criacao']
    search_fields = ['nome_empresa', 'cnpj', 'email']
    readonly_fields = ['data_criacao', 'data_atualizacao']


@admin.register(TipoContato)
class TipoContatoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'data_criacao']
    search_fields = ['nome']


@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'email', 'telefone', 'cargo', 'tipo_contato', 'canal', 'conta', 'proprietario', 'data_criacao']
    list_filter = ['data_criacao', 'cargo', 'tipo_contato', 'canal']
    search_fields = ['nome', 'email', 'cargo']
    readonly_fields = ['data_criacao', 'data_atualizacao']


@admin.register(EstagioFunil)
class EstagioFunilAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'cor']
    list_filter = ['tipo']
    search_fields = ['nome']


@admin.register(Oportunidade)
class OportunidadeAdmin(admin.ModelAdmin):
    list_display = [
        'nome', 'valor_estimado', 'funil', 'estagio', 'conta',
        'data_fechamento_esperada', 'proprietario', 'data_criacao'
    ]
    list_filter = ['funil', 'estagio', 'data_criacao', 'data_fechamento_esperada']
    search_fields = ['nome', 'conta__nome_empresa', 'descricao']
    readonly_fields = ['data_criacao', 'data_atualizacao']


@admin.register(Atividade)
class AtividadeAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo', 'status', 'data_vencimento', 'proprietario', 'data_criacao']
    list_filter = ['tipo', 'status', 'data_criacao']
    search_fields = ['titulo', 'descricao']
    readonly_fields = ['data_criacao', 'data_atualizacao']


class DiagnosticoRespostaInline(admin.TabularInline):
    model = DiagnosticoResposta
    extra = 1


@admin.register(DiagnosticoPilar)
class DiagnosticoPilarAdmin(admin.ModelAdmin):
    list_display = ['nome', 'slug', 'ordem', 'cor']
    search_fields = ['nome']
    prepopulated_fields = {'slug': ('nome',)}


@admin.register(DiagnosticoPergunta)
class DiagnosticoPerguntaAdmin(admin.ModelAdmin):
    list_display = ['texto', 'pilar', 'ordem']
    list_filter = ['pilar']
    search_fields = ['texto']
    inlines = [DiagnosticoRespostaInline]


@admin.register(DiagnosticoResultado)
class DiagnosticoResultadoAdmin(admin.ModelAdmin):
    list_display = ['conta', 'oportunidade', 'data_conclusao']
    readonly_fields = ['conta', 'oportunidade', 'data_conclusao', 'respostas_detalhadas', 'pontuacao_por_pilar']
    
    def has_add_permission(self, request):
        return False


@admin.register(Plano)
class PlanoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'preco_mensal', 'preco_anual']
    search_fields = ['nome']


@admin.register(PlanoAdicional)
class PlanoAdicionalAdmin(admin.ModelAdmin):
    list_display = ['nome', 'preco', 'unidade']
    search_fields = ['nome']


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'usuario', 'acao', 'modelo', 'objeto_id', 'objeto_repr', 'ip_address']
    list_filter = ['acao', 'modelo', 'timestamp']
    search_fields = ['usuario__username', 'usuario__first_name', 'usuario__last_name', 'objeto_repr', 'observacao']
    readonly_fields = ['timestamp', 'usuario', 'acao', 'modelo', 'objeto_id', 'objeto_repr', 'alteracoes', 'ip_address', 'user_agent', 'observacao']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']

    def has_add_permission(self, request):
        # Não permite adicionar logs manualmente
        return False

    def has_change_permission(self, request, obj=None):
        # Não permite editar logs
        return False

    def has_delete_permission(self, request, obj=None):
        # Permite deletar logs apenas para superusuários
        return request.user.is_superuser
