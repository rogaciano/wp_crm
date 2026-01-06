from django.apps import AppConfig


class CrmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crm'
    verbose_name = 'CRM de Vendas'

    def ready(self):
        """Importa os signals quando o app estiver pronto"""
        import crm.signals  # noqa
