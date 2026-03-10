"""
Views para o módulo de Multiatendimento WhatsApp.
Endpoints REST para inbox de conversas por canal.
"""

import logging
from django.db.models import Max, Count, Q, Subquery, OuterRef
from django.db.models.functions import Coalesce
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import WhatsappMessage, Canal, Contato

logger = logging.getLogger(__name__)


class InboxConversasView(APIView):
    """
    GET /api/atendimento/conversas/

    Retorna lista de conversas agrupadas por número remetente,
    filtradas pelo canal do usuário logado (ou por canal_id para Admin).

    Query params:
        canal_id   (int, optional)   — Admin pode especificar canal
        funil_tipo (str, optional)   — VENDAS | SUPORTE | POS_VENDA
        search     (str, optional)   — filtra por número ou nome
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Resolve canal_id: Admin pode passar qualquer um; outros usam o próprio
        canal_id = request.query_params.get('canal_id')
        if user.perfil == 'ADMIN' or user.is_superuser:
            if canal_id:
                canal = Canal.objects.filter(id=canal_id).first()
            else:
                # Admin sem filtro: retorna todos os canais (agrupa por canal tbm)
                canal = None
        else:
            canal = getattr(user, 'canal', None)
            if not canal:
                return Response({'conversas': [], 'canal': None})
            canal_id = canal.id

        # Base queryset: mensagens do canal (filtra por instancia)
        qs = WhatsappMessage.objects.all()

        if canal:
            qs = qs.filter(instancia=canal.evolution_instance_name)
        elif canal_id:
            canal_obj = Canal.objects.filter(id=canal_id).first()
            if canal_obj:
                qs = qs.filter(instancia=canal_obj.evolution_instance_name)

        # Filtro por funil_tipo
        funil_tipo = request.query_params.get('funil_tipo')
        if funil_tipo:
            qs = qs.filter(oportunidade__funil__tipo=funil_tipo)

        # Busca por número
        search = request.query_params.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(numero_remetente__icontains=search) |
                Q(numero_destinatario__icontains=search)
            )

        # Agrupa por número remetente (contatos que enviaram para nós)
        # Exclui mensagens que "nós" enviamos como remetente
        qs_recebidas = qs.filter(de_mim=False)

        # Pega números únicos com última mensagem e contagem de não lidas
        numeros = (
            qs_recebidas
            .values('numero_remetente')
            .annotate(
                ultima_timestamp=Max('timestamp'),
                nao_lidas=Count('id', filter=Q(lida=False)),
            )
            .order_by('-ultima_timestamp')[:100]
        )

        conversas = []
        for item in numeros:
            numero = item['numero_remetente']

            # Última mensagem (pode ser recebida ou enviada)
            ultima_msg = (
                qs.filter(
                    Q(numero_remetente=numero) | Q(numero_destinatario=numero)
                )
                .order_by('-timestamp')
                .values('texto', 'tipo_mensagem', 'de_mim', 'timestamp', 'oportunidade_id')
                .first()
            )

            # Tenta resolver nome do contato
            contato = (
                Contato.objects
                .filter(
                    Q(celular__icontains=numero[-8:]) |
                    Q(telefone__icontains=numero[-8:])
                )
                .values('id', 'nome')
                .first()
            )

            # Funil tipo (da oportunidade vinculada)
            oportunidade_id = ultima_msg.get('oportunidade_id') if ultima_msg else None
            funil_tipo_conv = None
            if oportunidade_id:
                from .models import Oportunidade
                opp = Oportunidade.objects.filter(id=oportunidade_id).select_related('funil').first()
                if opp and opp.funil:
                    funil_tipo_conv = opp.funil.tipo

            texto_preview = ''
            if ultima_msg:
                texto = ultima_msg.get('texto') or ''
                tipo = ultima_msg.get('tipo_mensagem', 'text')
                if tipo == 'audio':
                    texto_preview = '🎤 Áudio'
                elif tipo == 'image':
                    texto_preview = '📷 Imagem'
                elif tipo == 'document':
                    texto_preview = '📄 Documento'
                else:
                    texto_preview = texto[:80]

            conversas.append({
                'numero': numero,
                'nome_contato': contato['nome'] if contato else numero,
                'contato_id': contato['id'] if contato else None,
                'ultima_mensagem': texto_preview,
                'ultima_mensagem_timestamp': item['ultima_timestamp'].isoformat() if item['ultima_timestamp'] else None,
                'de_mim': ultima_msg.get('de_mim', False) if ultima_msg else False,
                'nao_lidas': item['nao_lidas'],
                'oportunidade_id': oportunidade_id,
                'funil_tipo': funil_tipo_conv,
                'canal_id': canal.id if canal else None,
            })

        return Response({
            'conversas': conversas,
            'canal': {
                'id': canal.id,
                'nome': canal.nome,
                'numero': canal.evolution_phone_number,
            } if canal else None,
        })


class InboxCanaisView(APIView):
    """
    GET /api/atendimento/canais/
    Lista canais disponíveis para o seletor (Admin only).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.perfil == 'ADMIN' or user.is_superuser:
            canais = Canal.objects.filter(
                evolution_instance_name__isnull=False
            ).exclude(evolution_instance_name='').values(
                'id', 'nome', 'evolution_phone_number', 'evolution_is_connected'
            )
            return Response({'canais': list(canais)})

        # Usuário normal: retorna apenas o seu canal
        canal = getattr(user, 'canal', None)
        if canal:
            return Response({'canais': [{
                'id': canal.id,
                'nome': canal.nome,
                'numero': canal.evolution_phone_number,
                'conectado': canal.evolution_is_connected,
            }]})
        return Response({'canais': []})
