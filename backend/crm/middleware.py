"""
Middleware para capturar informações de contexto para logs
"""
import threading

# Thread-local storage para armazenar request
_thread_locals = threading.local()


def get_current_request():
    """Retorna o request atual da thread"""
    return getattr(_thread_locals, 'request', None)


def get_current_user():
    """Retorna o usuário atual da thread"""
    request = get_current_request()
    if request and hasattr(request, 'user'):
        return request.user if request.user.is_authenticated else None
    return None


class CurrentUserMiddleware:
    """
    Middleware que captura o request atual e o armazena em thread-local storage,
    permitindo que os signals tenham acesso ao usuário e request.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Armazena o request no thread-local storage
        _thread_locals.request = request

        response = self.get_response(request)

        # Limpa o request após a resposta
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request

        return response


class ModelAuditMiddleware:
    """
    Middleware que injeta informações de usuário e request nos modelos
    antes de salvá-los, para que os signals possam acessar essas informações.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Adiciona método para injetar contexto nos modelos
        def inject_context(instance):
            """Injeta usuário e request no model instance"""
            if hasattr(request, 'user') and request.user.is_authenticated:
                instance._current_user = request.user
            instance._current_request = request

        # Armazena a função no request para ser usada nas views
        request.inject_audit_context = inject_context

        response = self.get_response(request)

        return response
