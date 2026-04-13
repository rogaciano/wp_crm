
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from crm.models import Funil, Oportunidade
funil_pe = Funil.objects.get(nome='Pernambuco CRM')
op = Oportunidade.objects.get(id=1043)

from rest_framework.test import APIRequestFactory
from crm.views import OportunidadeViewSet
from django.contrib.auth import get_user_model
User = get_user_model()

user = op.proprietario
factory = APIRequestFactory()
request = factory.get(f'/api/oportunidades/kanban/?funil_id={funil_pe.id}')
from rest_framework.request import Request

class DummyRequest(Request):
    def __init__(self, req):
        super().__init__(req)
        self.user = user
req = DummyRequest(request)

view = OportunidadeViewSet.as_view({'get': 'kanban'})
response = view(req)
for col in response.data:
    ops = col.get('oportunidades', col.get('items', []))
    for o in ops:
        if o['id'] == 1043:
            print('#########################')
            print('ACHOU OP 1043 NO KANBAN!')
            print('#########################')
            sys.exit(0)
print('OP nao encontrada no Kanban.')
