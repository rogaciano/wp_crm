import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from crm.serializers import ContatoSerializer
from crm.models import Conta
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()

conta = Conta.objects.first()

data = {
    'nome': 'Thais Marien',
    'conta': conta.id if conta else None,
    'telefones_input': [{'numero': '(81) 9 9232-8190', 'tipo': 'CELULAR', 'principal': True}],
    'tags_input': [],
    'notas': 'trabalha com fardamentos'
}

class DummyContext:
    def __init__(self, user, data):
        self.user = user
        self.data = data
        
class DummyRequest:
    def __init__(self, user, data):
        self.user = user
        self.data = data

context = {'request': DummyRequest(user, data)}
serializer = ContatoSerializer(data=data, context=context)

if serializer.is_valid():
    print("Contato VÁLIDO")
else:
    print("Contato INVÁLIDO:", serializer.errors)
