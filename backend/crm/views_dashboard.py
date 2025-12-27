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
        lead_filter = Q(data_criacao__gte=data_inicio)
        opp_filter = Q(data_criacao__gte=data_inicio)
        
        if user.perfil == 'RESPONSAVEL':
            lead_filter &= Q(proprietario__canal=user.canal)
            opp_filter &= Q(proprietario__canal=user.canal)
        elif user.perfil == 'VENDEDOR':
            lead_filter &= Q(proprietario=user)
            opp_filter &= Q(proprietario=user)

        # 1. KPIs Gerais (Cards)
        totais = Oportunidade.objects.filter(opp_filter).aggregate(
            receita_ganha=Sum('valor_estimado', filter=Q(estagio__tipo='GANHO')),
            pipeline_total=Sum('valor_estimado', filter=Q(estagio__tipo='ABERTO')),
            total_ganhas=Count('id', filter=Q(estagio__tipo='GANHO')),
            total_fechadas=Count('id', filter=Q(estagio__tipo__in=['GANHO', 'PERDIDO']))
        )

        receita = totais['receita_ganha'] or 0
        pipeline = totais['pipeline_total'] or 0
        ganhas = totais['total_ganhas'] or 0
        fechadas = totais['total_fechadas'] or 0
        
        win_rate = (ganhas / fechadas * 100) if fechadas > 0 else 0
        ticket_medio = (receita / ganhas) if ganhas > 0 else 0

        # 2. Funil de Vendas (Valor e Qtd por Estágio)
        funil = EstagioFunil.objects.order_by('ordem').annotate(
            valor=Sum('oportunidades__valor_estimado', filter=opp_filter),
            quantidade=Count('oportunidades', filter=opp_filter)
        ).values('nome', 'valor', 'quantidade', 'cor')

        # 3. Tendência de Leads e Negócios (Últimos 6 meses)
        seis_meses_atras = timezone.now() - timedelta(days=180)
        tendencia = Oportunidade.objects.filter(
            data_criacao__gte=seis_meses_atras
        ).annotate(
            mes=TruncMonth('data_criacao')
        ).values('mes').annotate(
            novas=Count('id'),
            ganhas=Count('id', filter=Q(estagio__tipo='GANHO')),
            valor=Sum('valor_estimado', filter=Q(estagio__tipo='GANHO'))
        ).order_by('mes')

        # 4. Origem de Leads (Top 5)
        origens = Lead.objects.filter(lead_filter).values('fonte').annotate(
            total=Count('id')
        ).order_by('-total')[:5]

        # 5. Maturidade por Pilar (Dados Ciência de Dados)
        # Pegamos os resultados dos diagnósticos vinculados aos leads desse usuário
        diag_filter = Q(data_conclusao__gte=data_inicio)
        if user.perfil == 'RESPONSAVEL':
            diag_filter &= Q(lead__proprietario__canal=user.canal)
        elif user.perfil == 'VENDEDOR':
            diag_filter &= Q(lead__proprietario=user)

        resultados = DiagnosticoResultado.objects.filter(diag_filter)
        maturidade_resumo = {}
        
        if resultados.exists():
            # Agregamos as notas de todos os pilares
            pilares_contagem = {}
            for res in resultados:
                # Segurança: verifica se o resultado tem as pontuações calculadas
                pontuacoes = res.pontuacao_por_pilar or {}
                for pilar, info in pontuacoes.items():
                    if isinstance(info, dict) and 'score' in info:
                        if pilar not in pilares_contagem:
                            pilares_contagem[pilar] = []
                        pilares_contagem[pilar].append(info['score'])
            
            for pilar, scores in pilares_contagem.items():
                if scores:
                    maturidade_resumo[pilar] = sum(scores) / len(scores)

        return Response({
            'kpis': {
                'receita_ganha': receita,
                'pipeline_ativo': pipeline,
                'win_rate': round(win_rate, 1),
                'ticket_medio': round(ticket_medio, 2),
                'leads_novos': Lead.objects.filter(lead_filter).count()
            },
            'funil': list(funil),
            'tendencia': list(tendencia),
            'origens': list(origens),
            'maturidade_media': maturidade_resumo
        })
