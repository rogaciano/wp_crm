"""
Views da API do CRM
"""
from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Canal, User, Lead, Conta, Contato, EstagioFunil, Oportunidade, Atividade,
    DiagnosticoPilar, DiagnosticoPergunta, DiagnosticoResposta, DiagnosticoResultado,
    Plano, PlanoAdicional
)
from .serializers import (
    CanalSerializer, UserSerializer, LeadSerializer, ContaSerializer,
    ContatoSerializer, EstagioFunilSerializer, OportunidadeSerializer,
    OportunidadeKanbanSerializer, AtividadeSerializer, LeadConversaoSerializer,
    DiagnosticoPilarSerializer, DiagnosticoResultadoSerializer, DiagnosticoPublicSubmissionSerializer,
    PlanoSerializer, PlanoAdicionalSerializer
)
from .services.ai_service import gerar_analise_diagnostico
from .permissions import HierarchyPermission, IsAdminUser


class CanalViewSet(viewsets.ModelViewSet):
    """ViewSet para Canais (apenas Admin)"""
    queryset = Canal.objects.all()
    serializer_class = CanalSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome']
    ordering_fields = ['nome', 'data_criacao']


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet para Usuários (apenas Admin)"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['perfil', 'canal', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'date_joined']
    
    @action(detail=False, methods=['get'], permission_classes=[HierarchyPermission])
    def me(self, request):
        """Retorna informações do usuário logado"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class LeadViewSet(viewsets.ModelViewSet):
    """ViewSet para Leads"""
    serializer_class = LeadSerializer
    permission_classes = [HierarchyPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'fonte']
    search_fields = ['nome', 'email', 'empresa']
    ordering_fields = ['nome', 'data_criacao']
    
    def get_queryset(self):
        """Aplica filtros de hierarquia"""
        user = self.request.user
        
        if user.perfil == 'ADMIN':
            return Lead.objects.all()
        elif user.perfil == 'RESPONSAVEL':
            return Lead.objects.filter(proprietario__canal=user.canal)
        else:  # VENDEDOR
            return Lead.objects.filter(proprietario=user)
    
    @action(detail=True, methods=['post'])
    def converter(self, request, pk=None):
        """Converte um Lead em Conta, Contato e opcionalmente Oportunidade"""
        lead = self.get_object()
        
        # Verifica se o lead já foi convertido
        if lead.status == Lead.STATUS_CONVERTIDO:
            return Response(
                {'error': 'Lead já foi convertido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = LeadConversaoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            with transaction.atomic():
                # Cria a Conta
                conta = Conta.objects.create(
                    nome_empresa=lead.empresa or f"Empresa de {lead.nome}",
                    telefone_principal=lead.telefone,
                    email=lead.email,
                    proprietario=lead.proprietario
                )
                
                # Cria o Contato
                contato = Contato.objects.create(
                    nome=lead.nome,
                    email=lead.email,
                    telefone=lead.telefone,
                    cargo=lead.cargo,
                    conta=conta,
                    proprietario=lead.proprietario
                )
                
                # Cria Oportunidade se solicitado
                oportunidade = None
                if serializer.validated_data.get('criar_oportunidade', False):
                    # Busca o primeiro estágio do funil
                    primeiro_estagio = EstagioFunil.objects.filter(
                        tipo=EstagioFunil.TIPO_ABERTO
                    ).first()
                    
                    if primeiro_estagio:
                        nome_oportunidade = serializer.validated_data.get(
                            'nome_oportunidade',
                            f"Oportunidade - {lead.nome}"
                        )
                        
                        oportunidade = Oportunidade.objects.create(
                            nome=nome_oportunidade,
                            valor_estimado=serializer.validated_data.get('valor_estimado'),
                            conta=conta,
                            contato_principal=contato,
                            estagio=primeiro_estagio,
                            proprietario=lead.proprietario
                        )
                
                # Marca o lead como convertido
                lead.status = Lead.STATUS_CONVERTIDO
                lead.save()
                
                # Vincula histórico de diagnósticos à nova Conta
                DiagnosticoResultado.objects.filter(lead=lead).update(conta=conta)
                
                return Response({
                    'message': 'Lead convertido com sucesso',
                    'conta_id': conta.id,
                    'contato_id': contato.id,
                    'oportunidade_id': oportunidade.id if oportunidade else None
                }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ContaViewSet(viewsets.ModelViewSet):
    """ViewSet para Contas"""
    serializer_class = ContaSerializer
    permission_classes = [HierarchyPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['setor', 'estado']
    search_fields = ['nome_empresa', 'cnpj', 'email']
    ordering_fields = ['nome_empresa', 'data_criacao']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.perfil == 'ADMIN':
            return Conta.objects.all()
        elif user.perfil == 'RESPONSAVEL':
            return Conta.objects.filter(proprietario__canal=user.canal)
        else:
            return Conta.objects.filter(proprietario=user)
    
    @action(detail=True, methods=['get'])
    def contatos(self, request, pk=None):
        """Lista contatos da conta"""
        conta = self.get_object()
        contatos = conta.contatos.all()
        serializer = ContatoSerializer(contatos, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def oportunidades(self, request, pk=None):
        """Lista oportunidades da conta"""
        conta = self.get_object()
        oportunidades = conta.oportunidades.all()
        serializer = OportunidadeSerializer(oportunidades, many=True, context={'request': request})
        return Response(serializer.data)


class ContatoViewSet(viewsets.ModelViewSet):
    """ViewSet para Contatos"""
    serializer_class = ContatoSerializer
    permission_classes = [HierarchyPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['conta', 'cargo']
    search_fields = ['nome', 'email', 'cargo']
    ordering_fields = ['nome', 'data_criacao']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.perfil == 'ADMIN':
            return Contato.objects.all()
        elif user.perfil == 'RESPONSAVEL':
            return Contato.objects.filter(proprietario__canal=user.canal)
        else:
            return Contato.objects.filter(proprietario=user)


class EstagioFunilViewSet(viewsets.ModelViewSet):
    """ViewSet para Estágios do Funil (Admin para CRUD, todos podem ler)"""
    queryset = EstagioFunil.objects.all()
    serializer_class = EstagioFunilSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['ordem']
    
    def get_permissions(self):
        """Admin pode modificar, outros só podem ler"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [HierarchyPermission()]


class OportunidadeViewSet(viewsets.ModelViewSet):
    """ViewSet para Oportunidades"""
    serializer_class = OportunidadeSerializer
    permission_classes = [HierarchyPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estagio', 'conta']
    search_fields = ['nome', 'conta__nome_empresa']
    ordering_fields = ['nome', 'valor_estimado', 'data_fechamento_esperada', 'data_criacao']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.perfil == 'ADMIN':
            return Oportunidade.objects.all()
        elif user.perfil == 'RESPONSAVEL':
            return Oportunidade.objects.filter(proprietario__canal=user.canal)
        else:
            return Oportunidade.objects.filter(proprietario=user)
    
    @action(detail=False, methods=['get'])
    def kanban(self, request):
        """Retorna oportunidades abertas agrupadas por estágio para visão Kanban"""
        queryset = self.get_queryset().filter(
            estagio__tipo=EstagioFunil.TIPO_ABERTO
        ).select_related('conta', 'contato_principal', 'estagio', 'proprietario')
        
        serializer = OportunidadeKanbanSerializer(queryset, many=True)
        
        # Agrupa por estágio
        estagios = EstagioFunil.objects.filter(tipo=EstagioFunil.TIPO_ABERTO)
        kanban_data = []
        
        for estagio in estagios:
            oportunidades = [
                opp for opp in serializer.data
                if opp['estagio'] == estagio.id
            ]
            kanban_data.append({
                'estagio': EstagioFunilSerializer(estagio).data,
                'oportunidades': oportunidades
            })
        
        return Response(kanban_data)
    
    @action(detail=True, methods=['patch'])
    def mudar_estagio(self, request, pk=None):
        """Muda o estágio de uma oportunidade (usado no drag-and-drop do Kanban)"""
        oportunidade = self.get_object()
        novo_estagio_id = request.data.get('estagio_id')
        
        if not novo_estagio_id:
            return Response(
                {'error': 'estagio_id é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            novo_estagio = EstagioFunil.objects.get(id=novo_estagio_id)
            oportunidade.estagio = novo_estagio
            
            # Se mudou para estágio fechado, registra a data
            if novo_estagio.tipo in [EstagioFunil.TIPO_GANHO, EstagioFunil.TIPO_PERDIDO]:
                from django.utils import timezone
                oportunidade.data_fechamento_real = timezone.now().date()
            
            oportunidade.save()
            
            serializer = self.get_serializer(oportunidade)
            return Response(serializer.data)
        
        except EstagioFunil.DoesNotExist:
            return Response(
                {'error': 'Estágio não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'])
    def gerar_texto_faturamento(self, request, pk=None):
        """Gera o texto formatado para faturamento"""
        opp = self.get_object()
        
        if not opp.plano:
            return Response({'error': 'Nenhum plano selecionado para esta oportunidade'}, status=status.HTTP_400_BAD_REQUEST)
            
        adicionais_texto = ""
        adicionais = opp.oportunidadeadicional_set.all()
        if adicionais.exists():
            adicionais_texto = "\n\nRecursos Adicionais Incluídos:\n"
            for ad in adicionais:
                adicionais_texto += f"• {ad.quantidade}x {ad.adicional.nome}\n"

        params = {
            'plano_nome': opp.plano.nome,
            'periodo': opp.get_periodo_pagamento_display(),
            'recursos': "\n".join(opp.plano.recursos),
            'adicionais': adicionais_texto,
            'cortesia': opp.cortesia or "Nenhuma cortesia registrada",
            'cliente_nome': opp.contato_principal.nome if opp.contato_principal else opp.conta.nome_empresa,
            'whatsapp': opp.contato_principal.telefone if opp.contato_principal else opp.conta.telefone_principal,
            'email': opp.contato_principal.email if opp.contato_principal else opp.conta.email,
            'mensalidade': f"R$ {opp.valor_estimado:,.2f}".replace('.', 'X').replace(',', '.').replace('X', ','),
            'label_investimento': 'Investimento Anual' if opp.periodo_pagamento == 'ANUAL' else 'Mensalidade',
            'cupom': opp.cupom_desconto or "Nenhum",
            'forma_pagamento': opp.get_forma_pagamento_display(),
            'vendedor': opp.proprietario.get_full_name(),
            'indicador': opp.indicador_comissao or "Direto",
            'suporte': opp.get_suporte_regiao_display() if opp.suporte_regiao else "N/A"
        }
        
        template = f"""
Por gentileza, realizar o faturamento da contratação abaixo:

Plano: {params['plano_nome']} ({params['periodo']})
{params['recursos']}{params['adicionais']}

Cortesia:
• {params['cortesia']}

Dados do cliente responsável pelo fechamento:
• Nome: {params['cliente_nome']}
• WhatsApp: {params['whatsapp']}
• E-mail: {params['email']}

Investimento:
• {params['label_investimento']}: {params['mensalidade']}
• Cupom de desconto: {params['cupom']}

• Forma de pagamento: {params['forma_pagamento']}
• Vendedor: {params['vendedor']}
• Indicador da comissão: {params['indicador']}
"""
        if opp.suporte_regiao:
            template += f"• Suporte: {params['suporte']}\n"
            
        template += "\nQualquer dúvida, estou a disposição!"
        
        return Response({'texto': template})


class PlanoViewSet(viewsets.ModelViewSet):
    """ViewSet para CRUD de Planos (Admin cria/edita, todos leem)"""
    queryset = Plano.objects.all()
    serializer_class = PlanoSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [HierarchyPermission()]


class PlanoAdicionalViewSet(viewsets.ModelViewSet):
    """ViewSet para CRUD de Adicionais de Plano (Admin cria/edita, todos leem)"""
    queryset = PlanoAdicional.objects.all()
    serializer_class = PlanoAdicionalSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [HierarchyPermission()]


class AtividadeViewSet(viewsets.ModelViewSet):
    """ViewSet para Atividades"""
    serializer_class = AtividadeSerializer
    permission_classes = [HierarchyPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo', 'status']
    search_fields = ['titulo', 'descricao']
    ordering_fields = ['data_vencimento', 'data_criacao']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.perfil == 'ADMIN':
            return Atividade.objects.all()
        elif user.perfil == 'RESPONSAVEL':
            return Atividade.objects.filter(proprietario__canal=user.canal)
        else:
            return Atividade.objects.filter(proprietario=user)
    
    @action(detail=True, methods=['post'])
    def concluir(self, request, pk=None):
        """Marca uma atividade como concluída"""
        atividade = self.get_object()
        
        from django.utils import timezone
        atividade.status = Atividade.STATUS_CONCLUIDA
        atividade.data_conclusao = timezone.now()
        atividade.save()
        
        serializer = self.get_serializer(atividade)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def content_types(self, request):
        """Retorna os tipos de objetos que podem ser associados a atividades"""
        from django.contrib.contenttypes.models import ContentType
        models_permitidos = ['lead', 'conta', 'contato', 'oportunidade']
        cts = ContentType.objects.filter(
            app_label='crm', 
            model__in=models_permitidos
        )
        return Response([
            {'id': ct.id, 'model': ct.model, 'nome': ct.model.capitalize()} 
            for ct in cts
        ])


class DiagnosticoViewSet(viewsets.ModelViewSet):
    """ViewSet para o Diagnóstico de Maturidade"""
    queryset = DiagnosticoResultado.objects.all()
    serializer_class = DiagnosticoResultadoSerializer
    
    def get_permissions(self):
        """Define permissões: perguntas e submeter são públicos"""
        if self.action in ['perguntas', 'submeter']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), HierarchyPermission()]

    def get_queryset(self):
        """Filtra resultados do diagnóstico baseado na hierarquia (após autenticado)"""
        user = self.request.user
        if not user.is_authenticated:
            return DiagnosticoResultado.objects.none()
            
        if user.perfil == 'ADMIN':
            return DiagnosticoResultado.objects.all()
        elif user.perfil == 'RESPONSAVEL':
            return DiagnosticoResultado.objects.filter(lead__proprietario__canal=user.canal)
        else:
            return DiagnosticoResultado.objects.filter(lead__proprietario=user)

    @action(detail=False, methods=['get'])
    def perguntas(self, request):
        """Retorna todos os pilares, perguntas e respostas para o frontend público"""
        pilares = DiagnosticoPilar.objects.all().prefetch_related('perguntas__respostas')
        serializer = DiagnosticoPilarSerializer(pilares, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def submeter(self, request):
        """Recebe as respostas do diagnóstico, cria o Lead e salva o resultado"""
        serializer = DiagnosticoPublicSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        respostas_ids = data['respostas_ids']
        
        # 1. Busca as respostas no banco para calcular a pontuação
        respostas_objs = DiagnosticoResposta.objects.filter(
            id__in=respostas_ids
        ).select_related('pergunta__pilar')
        
        if not respostas_objs.exists():
            return Response(
                {'error': 'Nenhuma resposta válida encontrada'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Processa pontuações por pilar
        pontuacao_por_pilar = {}
        respostas_detalhadas = []
        
        for r in respostas_objs:
            pilar_nome = r.pergunta.pilar.nome
            if pilar_nome not in pontuacao_por_pilar:
                pontuacao_por_pilar[pilar_nome] = {
                    'soma': 0,
                    'total_perguntas': 0,
                    'cor': r.pergunta.pilar.cor
                }
            
            pontuacao_por_pilar[pilar_nome]['soma'] += r.pontuacao
            pontuacao_por_pilar[pilar_nome]['total_perguntas'] += 1
            
            respostas_detalhadas.append({
                'pergunta': r.pergunta.texto,
                'pilar': pilar_nome,
                'resposta': r.texto,
                'pontos': r.pontuacao,
                'feedback': r.feedback
            })

        # Calcula a média (0-10) por pilar
        resultado_final = {}
        for pilar, dados in pontuacao_por_pilar.items():
            resultado_final[pilar] = {
                'score': round(dados['soma'] / dados['total_perguntas'], 1),
                'cor': dados['cor']
            }

        try:
            with transaction.atomic():
                # 3. Cria ou busca o Lead (pelo e-mail)
                admin_user = User.objects.filter(perfil='ADMIN', is_active=True).first()
                
                # Procura se já existe uma conta vinculada a esse e-mail via Contato
                conta_existente = None
                contato = Contato.objects.filter(email=data['email']).first()
                if contato:
                    conta_existente = contato.conta

                lead, created = Lead.objects.update_or_create(
                    email=data['email'],
                    defaults={
                        'nome': data['nome'],
                        'telefone': data.get('telefone', ''),
                        'empresa': data.get('empresa', ''),
                        'fonte': 'Diagnóstico de Maturidade',
                        'proprietario': admin_user
                    }
                )

                # 4. Salva o resultado do diagnóstico
                diagnostico = DiagnosticoResultado.objects.create(
                    lead=lead,
                    conta=conta_existente,  # Vincula à conta se o e-mail for de um cliente
                    respostas_detalhadas=respostas_detalhadas,
                    pontuacao_por_pilar=resultado_final
                )
                
                # 5. Gera Análise de IA (Pode demorar, em produção usar Celery)
                diagnostico.analise_ia = gerar_analise_diagnostico(diagnostico)
                diagnostico.save()

                return Response({
                    'message': 'Diagnóstico processado com sucesso',
                    'lead_id': lead.id,
                    'resultado': resultado_final,
                    'analise_ia': diagnostico.analise_ia
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response(
                {'error': f'Erro ao salvar diagnóstico: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
