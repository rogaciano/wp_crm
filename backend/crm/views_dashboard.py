from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django.db.models import Sum, Avg, Count, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
from .models import Lead, Conta, Contato, TipoContato, Canal, Oportunidade, Atividade, DiagnosticoResultado, EstagioFunil
from .permissions import HierarchyPermission

class DashboardViewSet(viewsets.ViewSet):
    """
    ViewSet para métricas e indicadores estratégicos (Dashboards)
    """
    permission_classes = [HierarchyPermission]

    def list(self, request):
        user = request.user
        periodo_dias = int(request.query_params.get('periodo', 30))
        data_inicio = timezone.now() - timedelta(days=periodo_dias)

        # Debug: Log do usuário e período
        print(f"Dashboard - Usuário: {user.username}, Perfil: {user.perfil}, Período: {periodo_dias} dias")

        # Filtros de Hierarquia base
        # 1. Filtro para coisas criadas no período (Leads novos)
        periodo_filter = Q(data_criacao__gte=data_inicio)
        
        # 2. Filtro para coisas fechadas no período (Receita, Win Rate)
        # Para receita ganha, vamos considerar oportunidades fechadas (GANHO) no período
        # OU oportunidades criadas no período que foram fechadas (mesmo sem data_fechamento_real)
        fechamento_filter = Q(
            estagio__tipo='GANHO',
            data_fechamento_real__gte=data_inicio.date()
        ) | Q(
            estagio__tipo='GANHO',
            data_fechamento_real__isnull=True,
            data_criacao__gte=data_inicio
        )
        
        # 3. Filtros de Hierarquia e Região (Segurança)
        # Filtro base: vale para quase tudo (Leads, Contas, Oportunidades, Atividades)
        base_hierarquia = Q()
        if user.perfil == 'ADMIN':
            # Admin vê tudo - não aplica filtro
            base_hierarquia = Q()
        elif user.perfil == 'RESPONSAVEL' and user.canal:
            base_hierarquia &= Q(proprietario__canal=user.canal)
        elif user.perfil == 'VENDEDOR':
            base_hierarquia &= Q(proprietario=user)
            
        # Filtro de canal: vale APENAS para Oportunidade
        # Admin não deve ter filtro de canal aplicado
        canal_filter = Q()
        if user.perfil != 'ADMIN' and user.canal:
            canal_filter &= Q(canal=user.canal)
        # Filtro completo para Oportunidades
        # Se base_hierarquia está vazio (ADMIN), não aplica filtro de hierarquia
        if user.perfil == 'ADMIN':
            opp_filter = canal_filter if canal_filter else Q()
        else:
            opp_filter = base_hierarquia & canal_filter
        
        print(f"Filtros - base_hierarquia: {base_hierarquia}, canal_filter: {canal_filter}")
        
        # Versão do filtro para uso em modelos relacionados (ex: EstagioFunil -> Oportunidades)
        def prefix_q(q_obj, prefix):
            if not q_obj: return Q()
            new_q = Q()
            for child in q_obj.children:
                if isinstance(child, tuple):
                    new_q &= Q(**{f"{prefix}{child[0]}": child[1]})
                else:
                    new_q &= prefix_q(child, prefix)
            return new_q

        hierarquia_opp_prefixed = prefix_q(opp_filter, 'oportunidades__')

        # KPIs de Receita e Win Rate (Baseados no fechamento no período)
        # Para receita ganha, consideramos oportunidades GANHO fechadas no período
        opps_fechamento = Oportunidade.objects.filter(opp_filter & fechamento_filter)
        print(f"Oportunidades fechamento: {opps_fechamento.count()}")
        
        stats_fechamento = opps_fechamento.aggregate(
            receita_ganha=Sum('valor_estimado', filter=Q(estagio__tipo='GANHO')),
            total_ganhas=Count('id', filter=Q(estagio__tipo='GANHO')),
            total_fechadas=Count('id', filter=Q(estagio__tipo__in=['GANHO', 'PERDIDO']))
        )
        
        # Para win rate, precisamos contar todas as fechadas no período (GANHO + PERDIDO)
        fechamento_completo_filter = Q(
            estagio__tipo__in=['GANHO', 'PERDIDO'],
            data_fechamento_real__gte=data_inicio.date()
        ) | Q(
            estagio__tipo__in=['GANHO', 'PERDIDO'],
            data_fechamento_real__isnull=True,
            data_criacao__gte=data_inicio
        )
        stats_fechamento_completo = Oportunidade.objects.filter(opp_filter & fechamento_completo_filter).aggregate(
            total_fechadas=Count('id')
        )
        total_fechadas = stats_fechamento_completo['total_fechadas'] or 0

        # KPIs de Pipeline (Baseado no estado ATUAL, independente de quando foi criado)
        opps_pipeline = Oportunidade.objects.filter(opp_filter & Q(estagio__tipo='ABERTO'))
        print(f"Oportunidades pipeline: {opps_pipeline.count()}")
        
        stats_pipeline = opps_pipeline.aggregate(
            pipeline_total=Sum('valor_estimado'),
            total_abertas=Count('id')
        )

        receita = stats_fechamento['receita_ganha'] or 0
        ganhas = stats_fechamento['total_ganhas'] or 0
        fechadas = total_fechadas  # Usar o contador completo
        win_rate = (ganhas / fechadas * 100) if fechadas > 0 else 0
        ticket_medio = (receita / ganhas) if ganhas > 0 else 0
        
        print(f"KPIs - Receita: {receita}, Ganhas: {ganhas}, Fechadas: {fechadas}, Win Rate: {win_rate}%")
        print(f"Pipeline - Total: {stats_pipeline['pipeline_total']}, Abertas: {stats_pipeline['total_abertas']}")

        # 2. Funil de Vendas (Visão Global do Pipeline Atual)
        funil_query = EstagioFunil.objects.order_by('nome').annotate(
            valor=Sum('oportunidades__valor_estimado', filter=hierarquia_opp_prefixed & Q(oportunidades__estagio__tipo='ABERTO')),
            quantidade=Count('oportunidades', filter=hierarquia_opp_prefixed & Q(oportunidades__estagio__tipo='ABERTO'))
        )
        
        funil = []
        for item in funil_query:
            funil.append({
                'nome': item.nome,
                'valor': float(item.valor or 0),
                'quantidade': item.quantidade or 0,
                'cor': item.cor
            })

        # 3. Tendência de Vendas (Últimos 180 dias)
        tendencia = []
        try:
            seis_meses_atras = timezone.now() - timedelta(days=180)
            print(f"Calculando tendência - Período: últimos 180 dias (desde {seis_meses_atras.date()})")
            
            # Query para todas as oportunidades criadas nos últimos 180 dias
            # Se opp_filter está vazio (ADMIN sem região), não aplica filtro
            if opp_filter:
                opps_tendencia = Oportunidade.objects.filter(
                    opp_filter & Q(data_criacao__gte=seis_meses_atras)
                )
            else:
                opps_tendencia = Oportunidade.objects.filter(
                    Q(data_criacao__gte=seis_meses_atras)
                )
            print(f"Total de oportunidades no período de tendência: {opps_tendencia.count()}")
            
            tendencia_query = opps_tendencia.annotate(
                mes=TruncMonth('data_criacao')
            ).values('mes').annotate(
                novas=Count('id'),
                ganhas=Count('id', filter=Q(estagio__tipo='GANHO')),
                valor=Sum('valor_estimado', filter=Q(estagio__tipo='GANHO'))
            ).order_by('mes')
            
            print(f"Meses com dados na tendência: {tendencia_query.count()}")
            
            for item in tendencia_query:
                mes_str = item['mes'].isoformat() if item['mes'] else None
                tendencia.append({
                    'mes': mes_str,
                    'novas': item['novas'] or 0,
                    'ganhas': item['ganhas'] or 0,
                    'valor': float(item['valor'] or 0)
                })
                print(f"Mês {mes_str}: {item['novas']} novas, {item['ganhas']} ganhas, R$ {item['valor'] or 0}")
        except Exception as e:
            import traceback
            print(f"Erro ao calcular tendência: {e}")
            print(traceback.format_exc())
            tendencia = []

        # 4. Origem de Leads (Baseado no período selecionado)
        leads_query = Lead.objects.filter(base_hierarquia & periodo_filter) if base_hierarquia else Lead.objects.filter(periodo_filter)
        print(f"Leads no período: {leads_query.count()}")
        
        origens = leads_query.values('fonte').annotate(
            total=Count('id')
        ).order_by('-total')[:5]

        # 5. Maturidade por Pilar
        # Nota: DiagnosticoResultado não tem proprietario direto, ele se liga a Lead/Conta.
        # Por enquanto, filtramos apenas por data no dashboard executivo.
        resultados = DiagnosticoResultado.objects.filter(data_conclusao__gte=data_inicio)
        maturidade_resumo = {}
        if resultados.exists():
            pilares_contagem = {}
            for res in resultados:
                p = res.pontuacao_por_pilar or {}
                for pilar, info in p.items():
                    if isinstance(info, dict) and 'score' in info:
                        if pilar not in pilares_contagem: pilares_contagem[pilar] = []
                        pilares_contagem[pilar].append(info['score'])
            for pilar, scores in pilares_contagem.items():
                maturidade_resumo[pilar] = round(sum(scores) / len(scores), 1)

        # 6. Atividades Atrasadas e Ativas
        agora = timezone.now()
        atrasadas_q = Q(status='Pendente', data_vencimento__lt=agora)
        ativas_q = Q(status='Pendente')  # Todas as pendentes
        
        atividades_base = Atividade.objects.filter(base_hierarquia) if base_hierarquia else Atividade.objects.all()
        atrasadas_count = atividades_base.filter(atrasadas_q).count()
        ativas_count = atividades_base.filter(ativas_q).count()
        
        atrasadas_lista = atividades_base.filter(atrasadas_q).order_by('data_vencimento')[:5].values(
            'id', 'titulo', 'tipo', 'data_vencimento'
        )

        # 7. Contatos por Tipo de Contato
        contatos_base = Contato.objects.filter(base_hierarquia) if base_hierarquia else Contato.objects.all()
        contatos_por_tipo = TipoContato.objects.annotate(
            total=Count('contatos', filter=Q(contatos__in=contatos_base))
        ).filter(total__gt=0).order_by('-total').values('id', 'nome', 'emoji', 'total')
        
        # 8. Contatos por Canal
        contatos_por_canal = Canal.objects.annotate(
            total=Count('contatos', filter=Q(contatos__in=contatos_base))
        ).filter(total__gt=0).order_by('-total').values('id', 'nome', 'total')

        # 9. Vendas por Plano (Oportunidades GANHAS agrupadas por plano)
        from .models import Plano
        vendas_por_plano = Plano.objects.annotate(
            total_vendas=Count('oportunidades', filter=opp_filter & Q(oportunidades__estagio__tipo='GANHO')),
            valor_total=Sum('oportunidades__valor_estimado', filter=opp_filter & Q(oportunidades__estagio__tipo='GANHO'))
        ).filter(total_vendas__gt=0).order_by('-valor_total').values('id', 'nome', 'total_vendas', 'valor_total')

        resultado = {
            'kpis': {
                'receita_ganha': float(receita),
                'pipeline_ativo': float(stats_pipeline['pipeline_total'] or 0),
                'win_rate': round(win_rate, 1),
                'ticket_medio': round(ticket_medio, 2),
                'leads_novos': leads_query.count(),
                'atividades_ativas': ativas_count,
                'atividades_atrasadas': atrasadas_count
            },
            'funil': funil,
            'tendencia': tendencia,
            'origens': list(origens),
            'maturidade_media': maturidade_resumo,
            'atividades_atrasadas_lista': list(atrasadas_lista),
            'contatos_por_tipo': list(contatos_por_tipo),
            'contatos_por_canal': list(contatos_por_canal),
            'vendas_por_plano': list(vendas_por_plano)
        }
        
        print(f"Resultado final - KPIs: {resultado['kpis']}")
        print(f"Funil items: {len(funil)}, Tendência items: {len(tendencia)}, Origens: {len(origens)}")
        
        return Response(resultado)
