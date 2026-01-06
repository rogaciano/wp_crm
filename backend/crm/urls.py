"""
URLs da API do CRM
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CanalViewSet, UserViewSet, LeadViewSet, ContaViewSet,
    ContatoViewSet, EstagioFunilViewSet, OportunidadeViewSet, AtividadeViewSet,
    DiagnosticoViewSet, PlanoViewSet, PlanoAdicionalViewSet, FunilViewSet, TipoContatoViewSet,
    TipoRedeSocialViewSet, WhatsappViewSet, WhatsappWebhookView
)
from .views_dashboard import DashboardViewSet

router = DefaultRouter()
router.register(r'whatsapp', WhatsappViewSet, basename='whatsapp')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'funis', FunilViewSet, basename='funil')
router.register(r'canais', CanalViewSet, basename='canal')
router.register(r'usuarios', UserViewSet, basename='usuario')
router.register(r'leads', LeadViewSet, basename='lead')
router.register(r'contas', ContaViewSet, basename='conta')
router.register(r'contatos', ContatoViewSet, basename='contato')
router.register(r'tipos-contato', TipoContatoViewSet, basename='tipocontato')
router.register(r'tipos-rede-social', TipoRedeSocialViewSet, basename='tiporedesocial')
router.register(r'estagios-funil', EstagioFunilViewSet, basename='estagiofunil')
router.register(r'oportunidades', OportunidadeViewSet, basename='oportunidade')
router.register(r'atividades', AtividadeViewSet, basename='atividade')
router.register(r'diagnosticos', DiagnosticoViewSet, basename='diagnostico')
router.register(r'planos', PlanoViewSet, basename='plano')
router.register(r'adicionais-plano', PlanoAdicionalViewSet, basename='adicional-plano')

urlpatterns = [
    path('', include(router.urls)),
    path('webhooks/whatsapp/', WhatsappWebhookView.as_view(), name='whatsapp-webhook'),
]
