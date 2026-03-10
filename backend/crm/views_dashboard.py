from rest_framework import viewsets, permissions
from rest_framework.response import Response
from django.db.models import Sum, Avg, Count, Q, F
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta, date
from .models import Conta, Contato, TipoContato, Canal, Oportunidade, Atividade, DiagnosticoResultado, EstagioFunil, Plano, PlanoAdicional, OportunidadeAdicional
from .permissions import HierarchyPermission


def _calcular_periodo(modo, hoje=None):
    """
    Retorna (data_inicio, data_fim) para o período solicitado.
    Para 'comparativo' retorna também o período anterior equivalente.
    """
    if hoje is None:
        hoje = date.today()

    if modo == 'mes_anterior':
        primeiro_dia_mes_atual = hoje.replace(day=1)
        data_fim = primeiro_dia_mes_atual - timedelta(days=1)
        data_inicio = data_fim.replace(day=1)
        return data_inicio, data_fim, None, None

    elif modo == 'ano_atual':
        data_inicio = date(hoje.year, 1, 1)
        data_fim = hoje
        return data_inicio, data_fim, None, None

    elif modo == 'ano_anterior':
        data_inicio = date(hoje.year - 1, 1, 1)
        data_fim = date(hoje.year - 1, 12, 31)
        return data_inicio, data_fim, None, None

    elif modo == 'comparativo':
        # Ano atual até hoje vs mesmo período do ano anterior
        data_inicio = date(hoje.year, 1, 1)
        data_fim = hoje
        data_inicio_ant = date(hoje.year - 1, 1, 1)
        data_fim_ant = date(hoje.year - 1, hoje.month, hoje.day)
        return data_inicio, data_fim, data_inicio_ant, data_fim_ant

    else:  # mes_atual (padrão)
        data_inicio = hoje.replace(day=1)
        data_fim = hoje
        return data_inicio, data_fim, None, None


class DashboardViewSet(viewsets.ViewSet):
    """
    ViewSet para métricas e indicadores estratégicos (Dashboards)
    """
    permission_classes = [HierarchyPermission]

    def list(self, request):
        user = request.user
        canal_id = request.query_params.get('canal_id')

        # Novo sistema de período por modo (mantém retrocompatibilidade)
        periodo_modo = request.query_params.get('periodo_modo', None)
        if periodo_modo:
            hoje = date.today()
            dt_inicio, dt_fim, dt_inicio_ant, dt_fim_ant = _calcular_periodo(periodo_modo, hoje)
            data_inicio = timezone.make_aware(
                timezone.datetime.combine(dt_inicio, timezone.datetime.min.time())
            )
        else:
            periodo_dias = int(request.query_params.get('periodo', 30))
            data_inicio = timezone.now() - timedelta(days=periodo_dias)
            dt_inicio = data_inicio.date()
            dt_fim = date.today()
            dt_inicio_ant = None
            dt_fim_ant = None

        # Filtros de Hierarquia base
        # 1. Filtro para coisas criadas no período (Oportunidades novas)
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
            # Admin vê tudo - não aplica filtro, mas pode filtrar por canal se quiser
            base_hierarquia = Q()
            if canal_id:
                base_hierarquia = Q(proprietario__canal_id=canal_id)
        elif user.perfil == 'RESPONSAVEL' and user.canal:
            base_hierarquia &= Q(proprietario__canal=user.canal)
        elif user.perfil == 'VENDEDOR':
            base_hierarquia &= Q(proprietario=user)
            
        # Filtro de canal: vale APENAS para Oportunidade
        canal_filter = Q()
        if user.perfil == 'ADMIN' and canal_id:
            canal_filter = Q(canal_id=canal_id)
        elif user.perfil != 'ADMIN' and user.canal:
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

        # 4. Origem de Oportunidades (Baseado no período selecionado)
        opps_novas_query = Oportunidade.objects.filter(opp_filter & periodo_filter)
        print(f"Oportunidades novas no período: {opps_novas_query.count()}")
        
        origens = opps_novas_query.values('fonte').annotate(
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

        # ── Helper: monta filtro de fechamento GANHO dentro de um range de datas ──
        def _fechamento_range_filter(di, df, prefix=''):
            """Retorna Q para oportunidades GANHO fechadas entre di e df."""
            p = prefix
            return Q(**{f'{p}estagio__tipo': 'GANHO'}) & (
                Q(**{f'{p}data_fechamento_real__gte': di, f'{p}data_fechamento_real__lte': df}) |
                Q(**{f'{p}data_fechamento_real__isnull': True, f'{p}data_criacao__date__gte': di, f'{p}data_criacao__date__lte': df})
            )

        # 9. Vendas por Plano (GANHAS no período)
        def _vendas_por_plano(di, df):
            vf = _fechamento_range_filter(di, df, prefix='oportunidades__')
            if canal_id:
                vf &= Q(oportunidades__canal_id=canal_id)
            if hierarquia_opp_prefixed:
                vf &= hierarquia_opp_prefixed
            return list(
                Plano.objects.annotate(
                    total_vendas=Count('oportunidades', filter=vf),
                    valor_total=Sum('oportunidades__valor_estimado', filter=vf)
                ).filter(total_vendas__gt=0).order_by('-valor_total').values(
                    'id', 'nome', 'preco_mensal', 'total_vendas', 'valor_total'
                )
            )

        vendas_por_plano = _vendas_por_plano(dt_inicio, dt_fim)

        # 10. Vendas por Adicional (GANHAS no período)
        hierarquia_opp_adicional = prefix_q(opp_filter, 'oportunidade__')

        def _vendas_por_adicional(di, df):
            base = OportunidadeAdicional.objects.filter(
                _fechamento_range_filter(di, df, prefix='oportunidade__')
            )
            if canal_id:
                base = base.filter(oportunidade__canal_id=canal_id)
            if hierarquia_opp_adicional:
                base = base.filter(hierarquia_opp_adicional)
            return list(
                base.values(
                    'adicional__id', 'adicional__nome', 'adicional__preco', 'adicional__unidade'
                ).annotate(
                    total_vendas=Count('oportunidade', distinct=True),
                    total_quantidade=Sum('quantidade'),
                    valor_total=Sum(F('adicional__preco') * F('quantidade'))
                ).order_by('-valor_total')
            )

        vendas_por_adicional = _vendas_por_adicional(dt_inicio, dt_fim)

        # 11. Vendas por Canal (GANHAS no período)
        vendas_canal_filter = _fechamento_range_filter(dt_inicio, dt_fim, prefix='oportunidades__')
        vendas_por_canal = list(Canal.objects.annotate(
            total_vendas=Count('oportunidades', filter=vendas_canal_filter),
            valor_total=Sum('oportunidades__valor_estimado', filter=vendas_canal_filter)
        ).filter(total_vendas__gt=0).order_by('-valor_total').values('id', 'nome', 'total_vendas', 'valor_total'))

        # 12. Comparativo (período anterior) — só se modo = comparativo
        vendas_por_plano_anterior = []
        vendas_por_adicional_anterior = []
        kpis_anterior = {}
        if dt_inicio_ant and dt_fim_ant:
            vendas_por_plano_anterior = _vendas_por_plano(dt_inicio_ant, dt_fim_ant)
            vendas_por_adicional_anterior = _vendas_por_adicional(dt_inicio_ant, dt_fim_ant)
            # KPIs do período anterior para comparação
            fech_ant = _fechamento_range_filter(dt_inicio_ant, dt_fim_ant)
            opps_fech_ant = Oportunidade.objects.filter(opp_filter & fech_ant)
            stats_ant = opps_fech_ant.aggregate(
                receita_ganha=Sum('valor_estimado'),
                total_ganhas=Count('id'),
            )
            kpis_anterior = {
                'receita_ganha': float(stats_ant['receita_ganha'] or 0),
                'total_ganhas': stats_ant['total_ganhas'] or 0,
            }

        resultado = {
            'kpis': {
                'receita_ganha': float(receita),
                'pipeline_ativo': float(stats_pipeline['pipeline_total'] or 0),
                'win_rate': round(win_rate, 1),
                'ticket_medio': round(ticket_medio, 2),
                'opps_novas': opps_novas_query.count(),
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
            'vendas_por_plano': vendas_por_plano,
            'vendas_por_adicional': vendas_por_adicional,
            'vendas_por_canal': vendas_por_canal,
            'periodo_info': {
                'modo': periodo_modo or 'legacy',
                'inicio': str(dt_inicio),
                'fim': str(dt_fim),
                'inicio_anterior': str(dt_inicio_ant) if dt_inicio_ant else None,
                'fim_anterior': str(dt_fim_ant) if dt_fim_ant else None,
            },
        }

        # Dados comparativos (só presentes no modo comparativo)
        if dt_inicio_ant:
            resultado['vendas_por_plano_anterior'] = vendas_por_plano_anterior
            resultado['vendas_por_adicional_anterior'] = vendas_por_adicional_anterior
            resultado['kpis_anterior'] = kpis_anterior
        
        return Response(resultado)
