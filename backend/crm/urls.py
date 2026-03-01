"""
URLs da API do CRM
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CanalViewSet, UserViewSet, ContaViewSet, OrigemViewSet,
    ContatoViewSet, EstagioFunilViewSet, OportunidadeViewSet, AtividadeViewSet,
    DiagnosticoViewSet, PlanoViewSet, PlanoAdicionalViewSet, FunilViewSet, TipoContatoViewSet,
    TipoRedeSocialViewSet, WhatsappViewSet, WhatsappWebhookView, LogViewSet, OrganogramaViewSet,
    TagViewSet, OportunidadeAnexoViewSet, TimelineViewSet, ContaMapaView, MapaCanalView
)
from .views_dashboard import DashboardViewSet

router = DefaultRouter()
router.register(r'whatsapp', WhatsappViewSet, basename='whatsapp')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'funis', FunilViewSet, basename='funil')
router.register(r'canais', CanalViewSet, basename='canal')
router.register(r'origens', OrigemViewSet, basename='origem')
router.register(r'usuarios', UserViewSet, basename='usuario')

router.register(r'contas', ContaViewSet, basename='conta')
router.register(r'contatos', ContatoViewSet, basename='contato')
router.register(r'tipos-contato', TipoContatoViewSet, basename='tipocontato')
router.register(r'tipos-rede-social', TipoRedeSocialViewSet, basename='tiporedesocial')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'estagios-funil', EstagioFunilViewSet, basename='estagiofunil')
router.register(r'oportunidades', OportunidadeViewSet, basename='oportunidade')
router.register(r'oportunidade-anexos', OportunidadeAnexoViewSet, basename='oportunidade-anexo')
router.register(r'atividades', AtividadeViewSet, basename='atividade')
router.register(r'diagnosticos', DiagnosticoViewSet, basename='diagnostico')
router.register(r'planos', PlanoViewSet, basename='plano')
router.register(r'adicionais-plano', PlanoAdicionalViewSet, basename='adicional-plano')
router.register(r'logs', LogViewSet, basename='log')
router.register(r'timeline', TimelineViewSet, basename='timeline')
router.register(r'organograma', OrganogramaViewSet, basename='organograma')

urlpatterns = [
    path('', include(router.urls)),
    path('webhooks/whatsapp/', WhatsappWebhookView.as_view(), name='whatsapp-webhook'),
    path('webhook/whatsapp/', WhatsappWebhookView.as_view(), name='whatsapp-webhook-alias'),  # alias sem 's'
    path('contas/mapa/', ContaMapaView.as_view(), name='contas-mapa'),
    path('mapa/canal/', MapaCanalView.as_view(), name='mapa-canal'),
]

