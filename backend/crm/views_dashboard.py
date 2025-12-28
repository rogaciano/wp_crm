from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django.db.models import Sum, Avg, Count, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
from .models import Lead, Conta, Oportunidade, Atividade, DiagnosticoResultado, EstagioFunil
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

        # Filtros de Hierarquia base
        # 1. Filtro para coisas criadas no período (Leads novos)
        periodo_filter = Q(data_criacao__gte=data_inicio)
        
        # 2. Filtro para coisas fechadas no período (Receita, Win Rate)
        # Fallback: Se data_fechamento_real for nula, tentamos usar data_criacao como aproximação
        # Isso ajuda a mostrar dados existentes que não tiveram a data de fechamento gravada.
        fechamento_filter = Q(data_fechamento_real__gte=data_inicio.date()) | \
                           Q(data_fechamento_real__isnull=True, data_criacao__gte=data_inicio)
        
        # 3. Filtros de Hierarquia e Região (Segurança)
        # Filtro base: vale para quase tudo (Leads, Contas, Oportunidades, Atividades)
        base_hierarquia = Q()
        if user.perfil == 'RESPONSAVEL' and user.canal:
            base_hierarquia &= Q(proprietario__canal=user.canal)
        elif user.perfil == 'VENDEDOR':
            base_hierarquia &= Q(proprietario=user)
            
        # Filtro de região: vale APENAS para Oportunidade (neste momento)
        regiao_filter = Q()
        if user.suporte_regiao:
            regiao_filter &= Q(suporte_regiao=user.suporte_regiao)

        # Filtro completo para Oportunidades
        opp_filter = base_hierarquia & regiao_filter

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
        stats_fechamento = Oportunidade.objects.filter(opp_filter & fechamento_filter).aggregate(
            receita_ganha=Sum('valor_estimado', filter=Q(estagio__tipo__iexact='GANHO')),
            total_ganhas=Count('id', filter=Q(estagio__tipo__iexact='GANHO')),
            total_fechadas=Count('id', filter=Q(estagio__tipo__iexact__in=['GANHO', 'PERDIDO']))
        )

        # KPIs de Pipeline (Baseado no estado ATUAL, independente de quando foi criado)
        stats_pipeline = Oportunidade.objects.filter(opp_filter & Q(estagio__tipo__iexact='ABERTO')).aggregate(
            pipeline_total=Sum('valor_estimado'),
            total_abertas=Count('id')
        )

        receita = stats_fechamento['receita_ganha'] or 0
        ganhas = stats_fechamento['total_ganhas'] or 0
        fechadas = stats_fechamento['total_fechadas'] or 0
        win_rate = (ganhas / fechadas * 100) if fechadas > 0 else 0
        ticket_medio = (receita / ganhas) if ganhas > 0 else 0

        # 2. Funil de Vendas (Visão Global do Pipeline Atual)
        funil_query = EstagioFunil.objects.order_by('ordem').annotate(
            valor=Sum('oportunidades__valor_estimado', filter=hierarquia_opp_prefixed & Q(oportunidades__estagio__tipo__iexact='ABERTO')),
            quantidade=Count('oportunidades', filter=hierarquia_opp_prefixed & Q(oportunidades__estagio__tipo__iexact='ABERTO'))
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
            tendencia_query = Oportunidade.objects.filter(
                opp_filter & Q(data_criacao__gte=seis_meses_atras)
            ).annotate(
                mes=TruncMonth('data_criacao')
            ).values('mes').annotate(
                novas=Count('id'),
                ganhas=Count('id', filter=Q(estagio__tipo__iexact='GANHO')),
                valor=Sum('valor_estimado', filter=Q(estagio__tipo__iexact='GANHO'))
            ).order_by('mes')
            
            for item in tendencia_query:
                tendencia.append({
                    'mes': item['mes'].isoformat() if item['mes'] else None,
                    'novas': item['novas'],
                    'ganhas': item['ganhas'],
                    'valor': float(item['valor'] or 0)
                })
        except Exception as e:
            print(f"Erro ao calcular tendência: {e}")
            tendencia = []

        # 4. Origem de Leads (Baseado no período selecionado)
        origens = Lead.objects.filter(base_hierarquia & periodo_filter).values('fonte').annotate(
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

        # 6. Atividades Atrasadas
        agora = timezone.now()
        atrasadas_q = Q(status='Pendente', data_vencimento__lt=agora)
        atrasadas_count = Atividade.objects.filter(base_hierarquia & atrasadas_q).count()
        atrasadas_lista = Atividade.objects.filter(base_hierarquia & atrasadas_q).order_by('data_vencimento')[:5].values(
            'id', 'titulo', 'tipo', 'data_vencimento'
        )

        return Response({
            'kpis': {
                'receita_ganha': float(receita),
                'pipeline_ativo': float(stats_pipeline['pipeline_total'] or 0),
                'win_rate': round(win_rate, 1),
                'ticket_medio': round(ticket_medio, 2),
                'leads_novos': Lead.objects.filter(base_hierarquia & periodo_filter).count(),
                'atividades_atrasadas': atrasadas_count
            },
            'funil': funil,
            'tendencia': tendencia,
            'origens': list(origens),
            'maturidade_media': maturidade_resumo,
            'atividades_atrasadas_lista': list(atrasadas_lista)
        })
