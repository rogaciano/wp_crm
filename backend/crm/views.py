"""
Views da API do CRM
"""
from rest_framework import viewsets, status, filters, permissions
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db import transaction
from django.db.models import Q, Sum, Count, Avg
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Canal, User, Lead, Conta, Contato, TipoContato, Funil, EstagioFunil, FunilEstagio, Oportunidade, Atividade,
    DiagnosticoPilar, DiagnosticoPergunta, DiagnosticoResposta, DiagnosticoResultado,
    Plano, PlanoAdicional, WhatsappMessage
)
from .serializers import (
    CanalSerializer, UserSerializer, LeadSerializer, ContaSerializer,
    ContatoSerializer, TipoContatoSerializer, EstagioFunilSerializer, FunilEstagioSerializer, OportunidadeSerializer,
    OportunidadeKanbanSerializer, AtividadeSerializer, LeadConversaoSerializer,
    DiagnosticoPilarSerializer, DiagnosticoResultadoSerializer, DiagnosticoPublicSubmissionSerializer,
    PlanoSerializer, PlanoAdicionalSerializer, FunilSerializer, WhatsappMessageSerializer
)
from .services.ai_service import gerar_analise_diagnostico
from .services.evolution_api import EvolutionService
from .permissions import HierarchyPermission, IsAdminUser
from django.utils import timezone
from django.conf import settings


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 1000


class CanalViewSet(viewsets.ModelViewSet):
    """ViewSet para Canais (CRUD apenas Admin, leitura para autenticados)"""
    serializer_class = CanalSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsAdminUser()]

    def get_queryset(self):
        user = self.request.user
        if user.perfil == 'ADMIN':
            return Canal.objects.all()
        
        # Responsável e Vendedor veem apenas o canal que pertencem 
        # ou que gerenciam (no caso do responsável)
        from django.db.models import Q
        q_filter = Q()
        if user.canal_id:
            q_filter |= Q(id=user.canal_id)
        
        if user.perfil == 'RESPONSAVEL':
            q_filter |= Q(responsavel=user)
            
        return Canal.objects.filter(q_filter).distinct()

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome']
    ordering_fields = ['nome', 'data_criacao']


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


class FunilViewSet(viewsets.ModelViewSet):
    """ViewSet para Funis"""
    serializer_class = FunilSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        # Admin vê todos para gestão
        if user.perfil == 'ADMIN':
            return Funil.objects.all()
        
        # Para outros perfis, vê funis que tem acesso explícito
        # Mas para garantir que Responsável e Vendedor vejam os funis básicos:
        funis_acesso = user.funis_acesso.filter(is_active=True)
        if not funis_acesso.exists() and user.perfil in ['RESPONSAVEL', 'VENDEDOR']:
            # Fallback para responsáveis e vendedores se não houver acesso explícito: 
            # vê funis ativos do sistema
            return Funil.objects.filter(is_active=True)
            
        return funis_acesso

    @action(detail=True, methods=['get'])
    def estagios(self, request, pk=None):
        """Lista estágios de um funil específico via tabela de ligação"""
        funil = self.get_object()
        vinculos = FunilEstagio.objects.filter(funil=funil).order_by('ordem')
        serializer = FunilEstagioSerializer(vinculos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def atualizar_estagios(self, request, pk=None):
        """Atualiza a lista de estágios e sua ordem para o funil"""
        funil = self.get_object()
        # Lista de dicionários [{'estagio_id': 1, 'ordem': 0, 'is_padrao': True}, ...]
        estagios_data = request.data.get('estagios', [])
        
        try:
            with transaction.atomic():
                # Remove vínculos atuais? 
                # (Melhor remover e recriar para garantir a ordem e seleção exata do usuário)
                FunilEstagio.objects.filter(funil=funil).delete()
                
                for item in estagios_data:
                    FunilEstagio.objects.create(
                        funil=funil,
                        estagio_id=item['estagio_id'],
                        ordem=item.get('ordem', 0),
                        is_padrao=item.get('is_padrao', False)
                    )
            
            return Response({'status': 'estágios atualizados'})
        except Exception as e:
            return Response({'error': str(e)}, status=400)


class LeadViewSet(viewsets.ModelViewSet):
    """ViewSet para Leads"""
    serializer_class = LeadSerializer
    permission_classes = [HierarchyPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'fonte', 'funil', 'estagio', 'canal']
    search_fields = ['nome', 'email', 'empresa']
    ordering_fields = ['nome', 'data_criacao']
    
    def get_queryset(self):
        """Aplica filtros de hierarquia e funis de acesso"""
        user = self.request.user
        
        if user.perfil == 'ADMIN':
            queryset = Lead.objects.all()
        elif user.perfil == 'RESPONSAVEL':
            # Vê leads do seu canal E de funis que tem acesso
            queryset = Lead.objects.filter(
                Q(canal=user.canal) | Q(proprietario__canal=user.canal)
            ).filter(funil__in=user.funis_acesso.all()).distinct()
        else:  # VENDEDOR
            # Vê seus leads (ou do canal se preferir, mas user disse 'vinculados aos seus Funis/canal')
            # Vou manter a trava de proprietário para vendedor mas adicionar funil_acesso
            queryset = Lead.objects.filter(
                proprietario=user,
                funil__in=user.funis_acesso.all()
            )
            
        return queryset.select_related('funil', 'estagio', 'proprietario', 'canal')

    def perform_create(self, serializer):
        # Se não forneceu estágio, busca o padrão do funil
        estagio = serializer.validated_data.get('estagio')
        funil = serializer.validated_data.get('funil')
        
        if not estagio and funil:
            vinculo_padrao = FunilEstagio.objects.filter(funil=funil, is_padrao=True).first()
            if not vinculo_padrao:
                # Se não houver marcado como padrão, pega o de menor ordem
                vinculo_padrao = FunilEstagio.objects.filter(funil=funil).order_by('ordem').first()
            
            if vinculo_padrao:
                estagio = vinculo_padrao.estagio
        
        # Atribui canal automaticamente se o usuário tiver um
        canal = serializer.validated_data.get('canal')
        if not canal and self.request.user.canal:
            canal = self.request.user.canal
            
        serializer.save(
            proprietario=self.request.user, 
            estagio=estagio,
            canal=canal
        )

    @action(detail=False, methods=['get'])
    def kanban(self, request):
        """Retorna leads agrupados por estágio para visão Kanban SDR"""
        funil_id = request.query_params.get('funil_id')
        
        # Filtros de hierarquia já no get_queryset
        queryset = self.get_queryset()
        
        if funil_id:
            queryset = queryset.filter(funil_id=funil_id)
        else:
            # Padrão: primeiro funil de leads disponível para o usuário
            user_funis = request.user.funis_acesso.filter(tipo=Funil.TIPO_LEAD) if request.user.perfil != 'ADMIN' else Funil.objects.filter(tipo=Funil.TIPO_LEAD)
            funil = user_funis.first()
            if funil:
                queryset = queryset.filter(funil=funil)
            else:
                return Response({'error': 'Nenhum funil de Leads associado ao usuário'}, status=400)
                
        # Agrupa por estágios do funil selecionado via tabela de ligação
        funil_selecionado_id = funil_id or (funil.id if 'funil' in locals() and funil else None)
        vinculos = FunilEstagio.objects.filter(funil_id=funil_selecionado_id).select_related('estagio').order_by('ordem')
        
        # Serializamos apenas os leads necessários
        serializer = LeadSerializer(queryset, many=True)
        
        kanban_data = []
        for vinculo in vinculos:
            leads_estagio = [
                lead for lead in serializer.data
                if lead.get('estagio') == vinculo.estagio_id
            ]
            # Montamos o objeto de estágio como o frontend espera
            estagio_data = EstagioFunilSerializer(vinculo.estagio).data
            estagio_data['ordem'] = vinculo.ordem
            estagio_data['is_padrao'] = vinculo.is_padrao
            
            kanban_data.append({
                'estagio': estagio_data,
                'items': leads_estagio
            })
            
        return Response(kanban_data)

    @action(detail=True, methods=['patch'])
    def mudar_estagio(self, request, pk=None):
        """Muda o estágio de um lead (usado no drag-and-drop do Kanban)"""
        lead = self.get_object()
        novo_estagio_id = request.data.get('estagio_id')
        
        if not novo_estagio_id:
            return Response(
                {'error': 'estagio_id é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                novo_estagio = EstagioFunil.objects.get(id=novo_estagio_id)
                lead.estagio = novo_estagio
                lead.save()
            
            serializer = LeadSerializer(lead)
            return Response(serializer.data)
        
        except EstagioFunil.DoesNotExist:
            return Response(
                {'error': 'Estágio não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
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
                nome_empresa = (lead.empresa or f"Empresa de {lead.nome}")[:255]
                conta = Conta.objects.create(
                    nome_empresa=nome_empresa,
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
                    # Busca o funil de destino (pode vir no request ou ser o padrão de vendas do user)
                    funil_id = request.data.get('funil_id')
                    if funil_id:
                        funil_venda = Funil.objects.get(id=funil_id)
                    else:
                        funil_venda = Funil.objects.filter(tipo=Funil.TIPO_OPORTUNIDADE).first()

                    if not funil_venda:
                        raise ValueError("Não foi possível criar a oportunidade: Nenhum funil de Vendas disponível.")

                    # Busca o estágio padrão DESTE funil
                    vinculo_estagio = FunilEstagio.objects.filter(funil=funil_venda, is_padrao=True).first() or \
                                     FunilEstagio.objects.filter(funil=funil_venda).order_by('ordem').first()
                    
                    if not vinculo_estagio:
                        raise ValueError(f"O funil '{funil_venda.nome}' não possui estágios configurados.")
                    
                    primeiro_estagio = vinculo_estagio.estagio
                    
                    nome_oportunidade = serializer.validated_data.get(
                        'nome_oportunidade',
                        f"Oportunidade - {lead.nome}"
                    )[:255]
                    
                    # Definir Canal: o informado no serializer ou o canal do proprietário do lead
                    canal_id = serializer.validated_data.get('canal')
                    canal_obj = Canal.objects.filter(id=canal_id).first() if canal_id else (lead.proprietario.canal if lead.proprietario else None)

                    oportunidade = Oportunidade.objects.create(
                        nome=nome_oportunidade,
                        valor_estimado=serializer.validated_data.get('valor_estimado'),
                        conta=conta,
                        contato_principal=contato,
                        estagio=primeiro_estagio,
                        proprietario=lead.proprietario,
                        canal=canal_obj
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
            import traceback
            print(f"Erro na conversão de lead: {str(e)}")
            traceback.print_exc()
            return Response(
                {'error': f'Falha na conversão: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['patch'])
    def mudar_estagio(self, request, pk=None):
        """Muda o estágio de um lead"""
        lead = self.get_object()
        novo_estagio_id = request.data.get('estagio_id') or request.data.get('estagio')
        
        if not novo_estagio_id:
            return Response({'error': 'estagio_id é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            estagio = EstagioFunil.objects.get(id=novo_estagio_id)
            lead.estagio = estagio
            lead.save()
            return Response(self.get_serializer(lead).data)
        except EstagioFunil.DoesNotExist:
            return Response({'error': 'Estágio não encontrado'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Retorna indicadores resumidos dos leads (KPIs)"""
        queryset = self.get_queryset()
        
        # Filtros de busca se enviados
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(nome__icontains=search) | 
                Q(email__icontains=search) | 
                Q(empresa__icontains=search)
            )
            
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        fonte_filter = request.query_params.get('fonte')
        if fonte_filter:
            queryset = queryset.filter(fonte=fonte_filter)

        total = queryset.count()
        leads_novos = queryset.filter(status=Lead.STATUS_NOVO).count()
        leads_qualificados = queryset.filter(status=Lead.STATUS_QUALIFICADO).count()
        leads_convertidos = queryset.filter(status=Lead.STATUS_CONVERTIDO).count()
        
        taxa_conversao = (leads_convertidos / total * 100) if total > 0 else 0
        
        return Response({
            'total': total,
            'novos': leads_novos,
            'qualificados': leads_qualificados,
            'convertidos': leads_convertidos,
            'taxa_conversao': round(taxa_conversao, 1)
        })


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
            return Conta.objects.filter(
                Q(proprietario__canal=user.canal) | Q(canal=user.canal)
            ).distinct()
        else: # VENDEDOR
            # Vê do seu canal
            return Conta.objects.filter(
                Q(proprietario__canal=user.canal) | Q(canal=user.canal)
            ).distinct()

    def perform_create(self, serializer):
        user = self.request.user
        canal = serializer.validated_data.get('canal')
        
        # Se não for ADMIN ou não forneceu canal, usa o do usuário
        if user.perfil != 'ADMIN' or not canal:
            canal = user.canal
            
        serializer.save(proprietario=user, canal=canal)
    
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


class TipoContatoViewSet(viewsets.ModelViewSet):
    """ViewSet para Tipos de Contato (CRUD apenas Admin, leitura para autenticados)"""
    queryset = TipoContato.objects.all()
    serializer_class = TipoContatoSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsAdminUser()]


class ContatoViewSet(viewsets.ModelViewSet):
    """ViewSet para Contatos"""
    serializer_class = ContatoSerializer
    permission_classes = [HierarchyPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['conta', 'tipo', 'tipo_contato', 'canal']
    search_fields = ['nome', 'email', 'conta__nome_empresa']
    ordering_fields = ['nome', 'data_criacao']
    
    def get_queryset(self):
        user = self.request.user
        
        if user.perfil == 'ADMIN':
            return Contato.objects.all()
        elif user.perfil in ['RESPONSAVEL', 'VENDEDOR']:
            # Vê contatos criados por ele/vendedores ou vinculados ao seu canal
            return Contato.objects.filter(
                Q(proprietario__canal=user.canal) | Q(canal=user.canal)
            ).distinct()
        return Contato.objects.filter(proprietario=user)

    def perform_create(self, serializer):
        user = self.request.user
        canal = serializer.validated_data.get('canal')
        
        # Se não for ADMIN ou não forneceu canal, usa o do usuário
        if user.perfil != 'ADMIN' or not canal:
            canal = user.canal
            
        serializer.save(proprietario=user, canal=canal)


class EstagioFunilViewSet(viewsets.ModelViewSet):
    """ViewSet para Definições de Estágios (Admin para CRUD, todos podem ler)"""
    queryset = EstagioFunil.objects.all()
    serializer_class = EstagioFunilSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo', 'funis_vinculados']
    search_fields = ['nome']
    ordering_fields = ['nome']
    
    def get_permissions(self):
        """Admin pode modificar, qualquer usuário autenticado pode ler"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        # Estágios são definições globais do sistema, qualquer usuário autenticado pode ler
        return [permissions.IsAuthenticated()]


class OportunidadeViewSet(viewsets.ModelViewSet):
    """ViewSet para Oportunidades"""
    serializer_class = OportunidadeSerializer
    permission_classes = [HierarchyPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estagio', 'conta', 'canal', 'funil']
    search_fields = ['nome', 'conta__nome_empresa']
    ordering_fields = ['nome', 'valor_estimado', 'data_fechamento_esperada', 'data_criacao']
    
    def get_queryset(self):
        """Aplica filtros de hierarquia e funis de acesso"""
        user = self.request.user
        
        if user.perfil == 'ADMIN':
            queryset = Oportunidade.objects.all()
        elif user.perfil == 'RESPONSAVEL':
            # Vê do seu canal (vínculo direto ou via proprietário) AND funis que tem acesso
            queryset = Oportunidade.objects.filter(
                Q(canal=user.canal) | Q(proprietario__canal=user.canal)
            ).filter(funil__in=user.funis_acesso.all()).distinct()
        else: # VENDEDOR
            # Mantemos a trava de proprietário mas adicionamos funis_acesso
            queryset = Oportunidade.objects.filter(
                proprietario=user,
                funil__in=user.funis_acesso.all()
            )
            
        return queryset.select_related('funil', 'estagio', 'conta', 'contato_principal', 'proprietario').prefetch_related('oportunidadeadicional_set')

    def perform_create(self, serializer):
        # Se não forneceu estágio, busca o padrão do funil
        estagio = serializer.validated_data.get('estagio')
        funil = serializer.validated_data.get('funil')
        
        if not estagio and funil:
            vinculo_padrao = FunilEstagio.objects.filter(funil=funil, is_padrao=True).first()
            if not vinculo_padrao:
                # Se não houver marcado como padrão, pega o de menor ordem
                vinculo_padrao = FunilEstagio.objects.filter(funil=funil).order_by('ordem').first()
            
            if vinculo_padrao:
                estagio = vinculo_padrao.estagio
        
        # Atribui canal automaticamente se o usuário tiver um
        canal = serializer.validated_data.get('canal')
        if not canal and self.request.user.canal:
            canal = self.request.user.canal
            
        # Garante que a conta da oportunidade também esteja vinculada ao mesmo canal
        # apenas se a conta ainda não tiver um canal definido
        conta = serializer.validated_data.get('conta')
        if conta and canal and not conta.canal:
            conta.canal = canal
            conta.save()
            
        serializer.save(
            proprietario=self.request.user, 
            estagio=estagio,
            canal=canal
        )
    
    @action(detail=False, methods=['get'])
    def kanban(self, request):
        """Retorna oportunidades abertas agrupadas por estágio para visão Kanban"""
        funil_id = request.query_params.get('funil_id')
        queryset = self.get_queryset().filter(
            estagio__tipo=EstagioFunil.TIPO_ABERTO
        )
        
        if funil_id:
            queryset = queryset.filter(funil_id=funil_id)
        else:
            # Se não informou, tenta o primeiro funil de oportunidades do usuário
            user_funis = request.user.funis_acesso.filter(tipo=Funil.TIPO_OPORTUNIDADE) if request.user.perfil != 'ADMIN' else Funil.objects.filter(tipo=Funil.TIPO_OPORTUNIDADE)
            funil = user_funis.first()
            if funil:
                queryset = queryset.filter(funil=funil)
                
        queryset = queryset.select_related('conta', 'contato_principal', 'estagio', 'proprietario')
        serializer = OportunidadeKanbanSerializer(queryset, many=True)
        
        # Agrupa por estágios do funil selecionado via tabela de ligação
        funil_selecionado_id = funil_id or (funil.id if 'funil' in locals() and funil else None)
        if funil_selecionado_id:
            vinculos = FunilEstagio.objects.filter(funil_id=funil_selecionado_id, estagio__tipo=EstagioFunil.TIPO_ABERTO).select_related('estagio').order_by('ordem')
        else:
            # Fallback se não houver funil (não deveria acontecer no Kanban novo)
            vinculos = FunilEstagio.objects.filter(estagio__tipo=EstagioFunil.TIPO_ABERTO).select_related('estagio').order_by('funil', 'ordem')
        
        kanban_data = []
        for vinculo in vinculos:
            oportunidades = [
                opp for opp in serializer.data
                if int(opp.get('estagio_id') or opp.get('estagio') or 0) == vinculo.estagio_id
            ]
            # Montamos o objeto de estágio como o frontend espera
            estagio_data = EstagioFunilSerializer(vinculo.estagio).data
            estagio_data['ordem'] = vinculo.ordem
            estagio_data['is_padrao'] = vinculo.is_padrao

            kanban_data.append({
                'estagio': estagio_data,
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
            with transaction.atomic():
                novo_estagio = EstagioFunil.objects.get(id=novo_estagio_id)
                oportunidade.estagio = novo_estagio
                
                # Se mudou para estágio fechado, registra a data
                if novo_estagio.tipo in [EstagioFunil.TIPO_GANHO, EstagioFunil.TIPO_PERDIDO]:
                    oportunidade.data_fechamento_real = timezone.now().date()
                
                oportunidade.save()
            
            # Usamos o KanbanSerializer para a resposta, pois é mais leve e o que o Kanban espera
            serializer = OportunidadeKanbanSerializer(oportunidade)
            return Response(serializer.data)
        
        except EstagioFunil.DoesNotExist:
            return Response(
                {'error': 'Estágio não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            # Captura erros inesperados para evitar 500 silencioso
            return Response(
                {'error': f'Erro ao mudar estágio: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Retorna indicadores resumidos das oportunidades (KPIs)"""
        queryset = self.get_queryset()
        
        # Filtros básicos de busca se enviados
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(nome__icontains=search) | 
                Q(conta__nome_empresa__icontains=search)
            )

        data = queryset.aggregate(
            total_valor=Sum('valor_estimado'),
            total_contagem=Count('id'),
            valor_medio=Avg('valor_estimado'),
            valor_ganho=Sum('valor_estimado', filter=Q(estagio__tipo='GANHO')),
            valor_aberto=Sum('valor_estimado', filter=Q(estagio__tipo='ABERTO')),
            contagem_aberta=Count('id', filter=Q(estagio__tipo='ABERTO')),
            contagem_ganha=Count('id', filter=Q(estagio__tipo='GANHO'))
        )
        
        # Formatar valores nulos para 0
        for key in data:
            if data[key] is None:
                data[key] = 0
        
        return Response(data)

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
            'indicador': opp.indicador_comissao.nome if opp.indicador_comissao else "Direto",
            'suporte': opp.canal.nome if opp.canal else "N/A"
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
        if opp.canal:
            template += f"• Suporte: {params['suporte']}\n"
            
        template += "\nQualquer dúvida, estou a disposição!"
        
        return Response({'texto': template})


class PlanoViewSet(viewsets.ModelViewSet):
    """ViewSet para CRUD de Planos (Admin cria/edita, todos leem)"""
    queryset = Plano.objects.all()
    serializer_class = PlanoSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsAdminUser()]


class PlanoAdicionalViewSet(viewsets.ModelViewSet):
    """ViewSet para CRUD de Adicionais de Plano (Admin cria/edita, todos leem)"""
    queryset = PlanoAdicional.objects.all()
    serializer_class = PlanoAdicionalSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsAdminUser()]


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
        if not atividade.data_conclusao:
            atividade.data_conclusao = timezone.now()
        atividade.save()
        
        serializer = self.get_serializer(atividade)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Retorna indicadores resumidos (pendentes e atrasadas)"""
        queryset = self.get_queryset()
        agora = timezone.now()
        
        total_pendentes = queryset.filter(status=Atividade.STATUS_PENDENTE).count()
        total_atrasadas = queryset.filter(
            status=Atividade.STATUS_PENDENTE, 
            data_vencimento__lt=agora
        ).count()
        
        return Response({
            'pendentes': total_pendentes,
            'atrasadas': total_atrasadas
        })

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
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
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class WhatsappViewSet(viewsets.ModelViewSet):
    """ViewSet para histórico e envio de mensagens WhatsApp"""
    queryset = WhatsappMessage.objects.all()
    serializer_class = WhatsappMessageSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['lead', 'oportunidade', 'numero_remetente', 'numero_destinatario']
    ordering_fields = ['timestamp']

    def get_queryset(self):
        import sys
        from django.conf import settings
        
        # Filtros de lead/oportunidade funcionam via DjangoFilterBackend
        # Mas o filtro de 'number' é customizado para pegar a conversa
        number = self.request.query_params.get('number')
        
        if number:
            # Limpa o número para pegar apenas dígitos
            clean_number = ''.join(filter(str.isdigit, str(number)))
            
            # Criamos variações do número para aumentar a chance de match
            # Ex: com 55, sem 55, com 9o dígito, sem 9o dígito
            variations = [clean_number]
            
            # Se for um número brasileiro sem 55
            if len(clean_number) >= 10 and not clean_number.startswith('55'):
                variations.append('55' + clean_number)
            
            # Se for um número brasileiro com 55
            if clean_number.startswith('55') and len(clean_number) >= 12:
                variations.append(clean_number[2:]) # Versão sem DDI
                
                # Lidar com o 9o dígito (específico do Brasil)
                # Formato: 55 + DDD (2) + 9 + Numero (8) = 13 dígitos
                if len(clean_number) == 13:
                    # Versão sem o 9
                    variations.append(clean_number[:4] + clean_number[5:])
                # Formato: 55 + DDD (2) + Numero (8) = 12 dígitos
                elif len(clean_number) == 12:
                    # Versão com o 9
                    variations.append(clean_number[:4] + '9' + clean_number[4:])
            
            # Remove duplicatas
            variations = list(set(variations))
            
            # Busca mensagens onde qualquer uma das variações aparece em remetente ou destinatário
            q_filter = Q()
            for v in variations:
                q_filter |= Q(numero_remetente__icontains=v)
                q_filter |= Q(numero_destinatario__icontains=v)
            
            queryset = self.queryset.filter(q_filter)
            
            # Opcional: Filtra pela instância atual para evitar mensagens de outras contas se houver
            # Mas geralmente no CRM queremos ver tudo que pertence a este contato
            
            return queryset.order_by('timestamp')

        return super().get_queryset()

    # ==================== ENDPOINTS DE CONEXÃO ====================

    @action(detail=False, methods=['get'])
    def status(self, request):
        """Retorna o status da conexão WhatsApp"""
        service = EvolutionService()
        result = service.get_connection_status()
        return Response(result)

    @action(detail=False, methods=['get'])
    def qrcode(self, request):
        """Retorna o QR Code para conexão"""
        service = EvolutionService()
        result = service.get_qr_code()
        return Response(result)

    @action(detail=False, methods=['post'])
    def connect(self, request):
        """Inicia o processo de conexão e retorna QR Code"""
        service = EvolutionService()
        
        # Primeiro verifica o status atual
        status_result = service.get_connection_status()
        
        if status_result.get('connected'):
            return Response({
                'success': True,
                'already_connected': True,
                'message': 'WhatsApp já está conectado',
                'status': status_result
            })
        
        # Se não está conectado, obtém o QR Code
        qr_result = service.get_qr_code()
        
        return Response({
            'success': qr_result.get('success', False),
            'already_connected': False,
            'qr_code': qr_result.get('qr_code'),
            'qr_base64': qr_result.get('qr_base64'),
            'status': status_result
        })

    @action(detail=False, methods=['post'])
    def disconnect(self, request):
        """Desconecta o WhatsApp"""
        service = EvolutionService()
        result = service.disconnect()
        return Response(result)

    @action(detail=False, methods=['post'])
    def restart(self, request):
        """Reinicia a instância"""
        service = EvolutionService()
        result = service.restart_instance()
        return Response(result)

    @action(detail=False, methods=['get'])
    def instance_info(self, request):
        """Retorna informações da instância"""
        service = EvolutionService()
        result = service.get_instance_info()
        return Response(result)

    # ==================== ENDPOINTS DE MENSAGEM ====================


    @action(detail=False, methods=['post'])
    def send(self, request):
        """Action para enviar mensagem através do CRM"""
        import uuid
        import sys
        
        # Log para debug
        print("=" * 50, file=sys.stderr)
        print("WHATSAPP SEND REQUEST RECEIVED", file=sys.stderr)
        print(f"request.data = {request.data}", file=sys.stderr)
        print("=" * 50, file=sys.stderr)
        
        number = request.data.get('number')
        text = request.data.get('text')
        lead_id = request.data.get('lead')
        opp_id = request.data.get('oportunidade')
        
        print(f"number={number}, text={text[:20] if text else None}..., lead_id={lead_id}, opp_id={opp_id}", file=sys.stderr)

        if not number or not text:
            return Response({'error': 'Número e texto são obrigatórios'}, status=400)

        service = EvolutionService()
        try:
            print(f"Tentando enviar para {number} via {service.base_url}", file=sys.stderr)
            result = service.send_text(number, text)
            print(f"Sucesso na API: {result}", file=sys.stderr)

            # Extrai ID da mensagem da resposta da Evolution API
            # A estrutura pode variar bastante, vamos tentar todos os formatos possíveis
            msg_id = None
            if isinstance(result, dict):
                # Tenta formato direto: { key: { id: "..." } }
                if 'key' in result and isinstance(result['key'], dict):
                    msg_id = result['key'].get('id')
                # Tenta formato aninhado: { data: { key: { id: "..." } } }
                elif 'data' in result and isinstance(result['data'], dict):
                    data_obj = result['data']
                    if 'key' in data_obj and isinstance(data_obj['key'], dict):
                        msg_id = data_obj['key'].get('id')
                # Tenta formato alternativo: { message: { key: { id: "..." } } }
                elif 'message' in result and isinstance(result['message'], dict):
                    if 'key' in result['message'] and isinstance(result['message']['key'], dict):
                        msg_id = result['message']['key'].get('id')

            # Log detalhado para debug
            print(f"[SEND] Estrutura da resposta: {list(result.keys()) if isinstance(result, dict) else 'not a dict'}", file=sys.stderr)
            print(f"[SEND] ID extraído: {msg_id}", file=sys.stderr)

            # Se não conseguiu extrair, gera um ID único local
            if not msg_id:
                msg_id = f"local_{uuid.uuid4().hex[:20]}"
                print(f"[SEND] ID não encontrado na resposta, usando ID local: {msg_id}", file=sys.stderr)
            
            # Formata o número para armazenamento consistente
            formatted_number = service._format_number(number)
            
            # Salva localmente
            msg = WhatsappMessage.objects.create(
                id_mensagem=msg_id,
                instancia=settings.EVOLUTION_INSTANCE_ID,
                de_mim=True,
                numero_remetente=settings.EVOLUTION_INSTANCE_ID,
                numero_destinatario=formatted_number,
                texto=text,
                timestamp=timezone.now(),
                lead_id=lead_id,
                oportunidade_id=opp_id
            )
            
            return Response(WhatsappMessageSerializer(msg).data)
        except Exception as e:
            import traceback
            print(f"ERRO NO VIEWSET: {str(e)}")
            traceback.print_exc()
            return Response({'error': str(e)}, status=500)

    @action(detail=False, methods=['post'])
    def sync(self, request):
        """
        Sincroniza mensagens da Evolution API para um número específico.
        Busca as mensagens mais recentes da API e importa as que ainda não existem.
        """
        import sys
        
        number = request.data.get('number')
        lead_id = request.data.get('lead')
        opp_id = request.data.get('oportunidade')
        limit = request.data.get('limit', 50)
        
        if not number:
            return Response({'error': 'Número é obrigatório'}, status=400)
        
        service = EvolutionService()
        
        try:
            print(f"[SYNC] Buscando mensagens para {number}...", file=sys.stderr)
            
            # Busca mensagens da API Evolution
            api_messages = service.find_messages(number, limit=limit)
            
            print(f"[SYNC] Resposta da API: {type(api_messages)}, len={len(api_messages) if isinstance(api_messages, list) else 'N/A'}", file=sys.stderr)
            
            # Se a resposta for um dict com 'messages', extrai a lista
            if isinstance(api_messages, dict):
                api_messages = api_messages.get('messages', api_messages.get('data', []))
            
            if not isinstance(api_messages, list):
                api_messages = []
            
            imported_count = 0
            skipped_count = 0
            
            for msg_data in api_messages:
                key = msg_data.get('key', {})
                id_msg = key.get('id')
                
                if not id_msg:
                    continue
                
                # Verifica se já existe
                if WhatsappMessage.objects.filter(id_mensagem=id_msg).exists():
                    skipped_count += 1
                    continue
                
                remote_jid = key.get('remoteJid', '')
                from_me = key.get('fromMe', False)
                
                # Extrai texto
                message_content = msg_data.get('message', {})
                text = ""
                if 'conversation' in message_content:
                    text = message_content['conversation']
                elif 'extendedTextMessage' in message_content:
                    text = message_content['extendedTextMessage'].get('text', '')
                
                # Mídia
                mtype = 'text'
                if not text:
                    for media_type in ['imageMessage', 'videoMessage', 'documentMessage', 'audioMessage']:
                        if media_type in message_content:
                            text = message_content[media_type].get('caption', f'[{media_type}]')
                            mtype = media_type.replace('Message', '')
                            break
                
                # Timestamp
                ts_int = msg_data.get('messageTimestamp')
                if ts_int:
                    dt = timezone.datetime.fromtimestamp(int(ts_int), tz=timezone.utc)
                else:
                    dt = timezone.now()
                
                # Determina remetente/destinatário
                remote_number = remote_jid.split('@')[0] if remote_jid else ''
                
                if from_me:
                    numero_remetente = settings.EVOLUTION_INSTANCE_ID
                    numero_destinatario = remote_number
                else:
                    numero_remetente = remote_number
                    numero_destinatario = settings.EVOLUTION_INSTANCE_ID
                
                # Cria a mensagem
                msg_obj = WhatsappMessage.objects.create(
                    id_mensagem=id_msg,
                    instancia=settings.EVOLUTION_INSTANCE_ID,
                    de_mim=from_me,
                    numero_remetente=numero_remetente,
                    numero_destinatario=numero_destinatario,
                    texto=text or '[sem texto]',
                    tipo_mensagem=mtype,
                    timestamp=dt,
                    lead_id=lead_id,
                    oportunidade_id=opp_id
                )
                
                # Tenta linkar com Lead/Oportunidade se não foi fornecido
                if not lead_id and not opp_id:
                    EvolutionService.identify_and_link_message(msg_obj)
                
                imported_count += 1
            
            print(f"[SYNC] Importadas: {imported_count}, Ignoradas (duplicatas): {skipped_count}", file=sys.stderr)
            
            return Response({
                'imported': imported_count,
                'skipped': skipped_count,
                'message': f'{imported_count} mensagens importadas, {skipped_count} já existiam'
            })
            
        except Exception as e:
            import traceback
            print(f"[SYNC] ERRO: {str(e)}", file=sys.stderr)
            traceback.print_exc()
            return Response({'error': str(e)}, status=500)


class WhatsappWebhookView(APIView):
    """Recebe notificações da Evolution API (MESSAGES_UPSERT)"""
    permission_classes = [permissions.AllowAny]  # Evolution envia sem auth JWT

    def post(self, request):
        import sys

        data = request.data
        event = data.get('event', '').lower()  # Normaliza para lowercase
        instance = data.get('instance', 'unknown')

        # Log para debug
        print(f"[WEBHOOK] Event: {event}, Instance: {instance}", file=sys.stderr)

        # Aceita mensagens recebidas/atualizadas e mensagens enviadas
        if event in ['messages.upsert', 'messages_upsert', 'send_message', 'messages.update', 'messages_update']:
            # A estrutura pode variar: data.messages ou data.data.messages
            messages_data = data.get('data', data)
            if isinstance(messages_data, dict):
                messages = messages_data.get('messages', [])
                # Para evento send_message, pode vir no formato diferente
                if not messages and 'message' in messages_data:
                    messages = [messages_data]
            else:
                messages = []

            print(f"[WEBHOOK] Processando {len(messages)} mensagens do evento '{event}'", file=sys.stderr)

            for msg_data in messages:
                try:
                    # Log da estrutura da mensagem para debug
                    print(f"[WEBHOOK] Estrutura da mensagem: {list(msg_data.keys())}", file=sys.stderr)

                    key = msg_data.get('key', {})
                    id_msg = key.get('id')

                    if not id_msg:
                        print(f"[WEBHOOK] Mensagem sem ID, ignorando. Keys: {list(msg_data.keys())}", file=sys.stderr)
                        continue
                    
                    remote_jid = key.get('remoteJid', '')
                    from_me = key.get('fromMe', False)
                    
                    # Previne duplicatas - verifica se já existe a mensagem com esse ID
                    existing_msg = WhatsappMessage.objects.filter(id_mensagem=id_msg).first()
                    if existing_msg:
                        print(f"[WEBHOOK] Mensagem {id_msg[:10]}... já existe (ID: {existing_msg.id}), ignorando", file=sys.stderr)
                        continue

                    # Extrai texto
                    message_content = msg_data.get('message', {})
                    text = ""
                    if 'conversation' in message_content:
                        text = message_content['conversation']
                    elif 'extendedTextMessage' in message_content:
                        text = message_content['extendedTextMessage'].get('text', '')
                    elif 'buttonsResponseMessage' in message_content:
                        text = message_content['buttonsResponseMessage'].get('selectedDisplayText', '')
                    
                    # Se for mídia, tenta pegar a legenda
                    mtype = 'text'
                    if not text:
                        for media_type in ['imageMessage', 'videoMessage', 'documentMessage', 'audioMessage']:
                            if media_type in message_content:
                                text = message_content[media_type].get('caption', f'[{media_type}]')
                                mtype = media_type.replace('Message', '')
                                break

                    # Timestamp
                    ts_int = msg_data.get('messageTimestamp')
                    if ts_int:
                        dt = timezone.datetime.fromtimestamp(int(ts_int), tz=timezone.utc)
                    else:
                        dt = timezone.now()

                    # Determina números
                    remote_number = remote_jid.split('@')[0] if remote_jid else ''
                    
                    if from_me:
                        numero_remetente = instance
                        numero_destinatario = remote_number
                    else:
                        numero_remetente = remote_number
                        numero_destinatario = instance

                    # Salva
                    msg_obj = WhatsappMessage.objects.create(
                        id_mensagem=id_msg,
                        instancia=instance,
                        de_mim=from_me,
                        numero_remetente=numero_remetente,
                        numero_destinatario=numero_destinatario,
                        texto=text or '[sem texto]',
                        tipo_mensagem=mtype,
                        timestamp=dt
                    )
                    
                    print(f"[WEBHOOK] Mensagem salva: {id_msg[:10]}... de_mim={from_me}", file=sys.stderr)
                    
                    # Tenta linkar com Lead/Oportunidade
                    EvolutionService.identify_and_link_message(msg_obj)
                    
                except Exception as e:
                    print(f"[WEBHOOK] Erro ao processar mensagem: {str(e)}", file=sys.stderr)
                    import traceback
                    traceback.print_exc()
                    continue

        return Response({'status': 'received'}, status=200)

