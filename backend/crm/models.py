"""
Modelos do Sistema CRM de Vendas
"""
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.core.validators import EmailValidator


class Canal(models.Model):
    """Representa um Canal de Vendas"""
    nome = models.CharField(max_length=100, unique=True)
    responsavel = models.OneToOneField(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='canal_responsavel'
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Canal'
        verbose_name_plural = 'Canais'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class User(AbstractUser):
    """Usuário customizado do sistema"""
    PERFIL_VENDEDOR = 'VENDEDOR'
    PERFIL_RESPONSAVEL = 'RESPONSAVEL'
    PERFIL_ADMIN = 'ADMIN'
    
    PERFIL_CHOICES = [
        (PERFIL_VENDEDOR, 'Vendedor'),
        (PERFIL_RESPONSAVEL, 'Responsável de Canal'),
        (PERFIL_ADMIN, 'Administrador'),
    ]
    
    perfil = models.CharField(
        max_length=20,
        choices=PERFIL_CHOICES,
        default=PERFIL_VENDEDOR
    )
    canal = models.ForeignKey(
        Canal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vendedores'
    )
    telefone = models.CharField(max_length=20, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_perfil_display()})"

    def save(self, *args, **kwargs):
        # Validação: Responsável e Vendedor devem ter um Canal
        if self.perfil in [self.PERFIL_RESPONSAVEL, self.PERFIL_VENDEDOR]:
            if not self.canal:
                raise ValueError(f"{self.get_perfil_display()} deve estar associado a um Canal")
        super().save(*args, **kwargs)


class Lead(models.Model):
    """Lead - Prospecto inicial não qualificado"""
    STATUS_NOVO = 'Novo'
    STATUS_CONTATADO = 'Contatado'
    STATUS_QUALIFICADO = 'Qualificado'
    STATUS_CONVERTIDO = 'Convertido'
    STATUS_DESCARTADO = 'Descartado'
    
    STATUS_CHOICES = [
        (STATUS_NOVO, 'Novo'),
        (STATUS_CONTATADO, 'Contatado'),
        (STATUS_QUALIFICADO, 'Qualificado'),
        (STATUS_CONVERTIDO, 'Convertido'),
        (STATUS_DESCARTADO, 'Descartado'),
    ]
    
    nome = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True, validators=[EmailValidator()])
    telefone = models.CharField(max_length=20, null=True, blank=True)
    empresa = models.CharField(max_length=255, null=True, blank=True)
    cargo = models.CharField(max_length=100, null=True, blank=True)
    fonte = models.CharField(max_length=100, null=True, blank=True, help_text='Ex: Site, Evento, Indicação')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NOVO)
    notas = models.TextField(null=True, blank=True)
    proprietario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='leads')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    # Relação polimórfica com Atividades
    atividades = GenericRelation('Atividade')

    class Meta:
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['proprietario', 'status']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f"{self.nome} - {self.status}"


class Conta(models.Model):
    """Conta - Representa uma empresa/organização"""
    nome_empresa = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=20, null=True, blank=True, unique=True)
    telefone_principal = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    setor = models.CharField(max_length=100, null=True, blank=True)
    
    # Endereço
    endereco = models.CharField(max_length=255, null=True, blank=True)
    cidade = models.CharField(max_length=100, null=True, blank=True)
    estado = models.CharField(max_length=2, null=True, blank=True)
    cep = models.CharField(max_length=10, null=True, blank=True)
    
    notas = models.TextField(null=True, blank=True)
    proprietario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='contas')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    # Relação polimórfica com Atividades
    atividades = GenericRelation('Atividade')

    class Meta:
        verbose_name = 'Conta'
        verbose_name_plural = 'Contas'
        ordering = ['nome_empresa']
        indexes = [
            models.Index(fields=['proprietario']),
            models.Index(fields=['cnpj']),
        ]

    def __str__(self):
        return self.nome_empresa


class Contato(models.Model):
    """Contato - Pessoa física vinculada a uma Conta"""
    nome = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True, validators=[EmailValidator()])
    telefone = models.CharField(max_length=20, null=True, blank=True)
    celular = models.CharField(max_length=20, null=True, blank=True)
    cargo = models.CharField(max_length=100, null=True, blank=True)
    departamento = models.CharField(max_length=100, null=True, blank=True)
    
    conta = models.ForeignKey(
        Conta,
        on_delete=models.CASCADE,
        related_name='contatos'
    )
    proprietario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='contatos')
    
    notas = models.TextField(null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    # Relação polimórfica com Atividades
    atividades = GenericRelation('Atividade')

    class Meta:
        verbose_name = 'Contato'
        verbose_name_plural = 'Contatos'
        ordering = ['nome']
        indexes = [
            models.Index(fields=['proprietario', 'conta']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f"{self.nome} ({self.conta.nome_empresa})"


class EstagioFunil(models.Model):
    """Estágio do Funil de Vendas"""
    TIPO_ABERTO = 'ABERTO'
    TIPO_GANHO = 'GANHO'
    TIPO_PERDIDO = 'PERDIDO'
    
    TIPO_CHOICES = [
        (TIPO_ABERTO, 'Aberto'),
        (TIPO_GANHO, 'Fechado - Ganho'),
        (TIPO_PERDIDO, 'Fechado - Perdido'),
    ]
    
    nome = models.CharField(max_length=100)
    ordem = models.PositiveIntegerField(default=0)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default=TIPO_ABERTO)
    cor = models.CharField(max_length=7, default='#3B82F6', help_text='Cor em hexadecimal')
    
    class Meta:
        verbose_name = 'Estágio do Funil'
        verbose_name_plural = 'Estágios do Funil'
        ordering = ['ordem']
        unique_together = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"


class Oportunidade(models.Model):
    """Oportunidade - Negócio/Venda em potencial"""
    nome = models.CharField(max_length=255)
    valor_estimado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    data_fechamento_esperada = models.DateField(null=True, blank=True)
    probabilidade = models.PositiveIntegerField(
        default=0,
        help_text='Probabilidade de fechamento (0-100%)'
    )
    
    estagio = models.ForeignKey(
        EstagioFunil,
        on_delete=models.PROTECT,
        related_name='oportunidades'
    )
    conta = models.ForeignKey(
        Conta,
        on_delete=models.CASCADE,
        related_name='oportunidades'
    )
    contato_principal = models.ForeignKey(
        Contato,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='oportunidades'
    )
    proprietario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='oportunidades'
    )
    
    descricao = models.TextField(null=True, blank=True)
    motivo_perda = models.TextField(null=True, blank=True)
    data_fechamento_real = models.DateField(null=True, blank=True)
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    # Relação polimórfica com Atividades
    atividades = GenericRelation('Atividade')

    class Meta:
        verbose_name = 'Oportunidade'
        verbose_name_plural = 'Oportunidades'
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['proprietario', 'estagio']),
            models.Index(fields=['conta']),
        ]

    def __str__(self):
        return f"{self.nome} - R$ {self.valor_estimado or 0}"


class Atividade(models.Model):
    """Atividade - Interação registrada (Tarefa, Ligação, Reunião, E-mail)"""
    TIPO_TAREFA = 'TAREFA'
    TIPO_LIGACAO = 'LIGACAO'
    TIPO_REUNIAO = 'REUNIAO'
    TIPO_EMAIL = 'EMAIL'
    TIPO_NOTA = 'NOTA'
    
    TIPO_CHOICES = [
        (TIPO_TAREFA, 'Tarefa'),
        (TIPO_LIGACAO, 'Ligação'),
        (TIPO_REUNIAO, 'Reunião'),
        (TIPO_EMAIL, 'E-mail'),
        (TIPO_NOTA, 'Nota'),
    ]
    
    STATUS_PENDENTE = 'Pendente'
    STATUS_CONCLUIDA = 'Concluída'
    STATUS_CANCELADA = 'Cancelada'
    
    STATUS_CHOICES = [
        (STATUS_PENDENTE, 'Pendente'),
        (STATUS_CONCLUIDA, 'Concluída'),
        (STATUS_CANCELADA, 'Cancelada'),
    ]
    
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    titulo = models.CharField(max_length=255)
    descricao = models.TextField(null=True, blank=True)
    data_vencimento = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDENTE)
    
    # Relação Polimórfica (pode ser associada a Lead, Conta, Contato ou Oportunidade)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    associado_a = GenericForeignKey('content_type', 'object_id')
    
    proprietario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='atividades'
    )
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    data_conclusao = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Atividade'
        verbose_name_plural = 'Atividades'
        ordering = ['-data_criacao']
        indexes = [
            models.Index(fields=['proprietario', 'status']),
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        return f"{self.get_tipo_display()}: {self.titulo}"


class DiagnosticoPilar(models.Model):
    """Pilar de análise do diagnóstico (ex: Produção, Vendas, Financeiro)"""
    nome = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    descricao = models.TextField(null=True, blank=True)
    ordem = models.PositiveIntegerField(default=0)
    cor = models.CharField(max_length=7, default='#3B82F6', help_text='Cor em hexadecimal para o gráfico')

    class Meta:
        verbose_name = 'Pilar do Diagnóstico'
        verbose_name_plural = 'Pilares do Diagnóstico'
        ordering = ['ordem']

    def __str__(self):
        return self.nome


class DiagnosticoPergunta(models.Model):
    """Pergunta do diagnóstico vinculada a um pilar"""
    pilar = models.ForeignKey(DiagnosticoPilar, on_delete=models.CASCADE, related_name='perguntas')
    texto = models.TextField()
    ordem = models.PositiveIntegerField(default=0)
    ajuda = models.TextField(null=True, blank=True, help_text='Texto de ajuda ou explicação da pergunta')

    class Meta:
        verbose_name = 'Pergunta do Diagnóstico'
        verbose_name_plural = 'Perguntas do Diagnóstico'
        ordering = ['pilar__ordem', 'ordem']

    def __str__(self):
        return f"[{self.pilar.nome}] {self.texto[:50]}..."


class DiagnosticoResposta(models.Model):
    """Opção de resposta para uma pergunta com sua respectiva pontuação"""
    pergunta = models.ForeignKey(DiagnosticoPergunta, on_delete=models.CASCADE, related_name='respostas')
    texto = models.TextField()
    pontuacao = models.IntegerField(default=0, help_text='Pontuação de 0 a 10')
    feedback = models.TextField(null=True, blank=True, help_text='Feedback específico para esta resposta')

    class Meta:
        verbose_name = 'Resposta do Diagnóstico'
        verbose_name_plural = 'Respostas do Diagnóstico'
        ordering = ['pergunta', 'pontuacao']

    def __str__(self):
        return f"{self.texto[:30]} ({self.pontuacao} pts)"


class DiagnosticoResultado(models.Model):
    """Resultado final do diagnóstico vinculado a um Lead ou Conta"""
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='diagnosticos', null=True, blank=True)
    conta = models.ForeignKey(Conta, on_delete=models.CASCADE, related_name='diagnosticos', null=True, blank=True)
    data_conclusao = models.DateTimeField(auto_now_add=True)
    
    # Armazena as respostas brutas para histórico
    respostas_detalhadas = models.JSONField(help_text='JSON com as perguntas e respostas escolhidas')
    
    # Armazena a pontuação processada por pilar para facilitar o gráfico
    pontuacao_por_pilar = models.JSONField(help_text='JSON com {pilar_nome: score}')
    
    # Análise textual gerada por IA
    analise_ia = models.TextField(null=True, blank=True, help_text='Análise estratégica gerada via IA')

    class Meta:
        verbose_name = 'Resultado do Diagnóstico'
        verbose_name_plural = 'Resultados do Diagnóstico'
        ordering = ['-data_conclusao']

    def __str__(self):
        entidade = self.lead.nome if self.lead else (self.conta.nome_empresa if self.conta else "N/A")
        return f"Diagnóstico: {entidade} em {self.data_conclusao.strftime('%d/%m/%Y')}"
