from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Canal, Funil, EstagioFunil, FunilEstagio, Conta, Oportunidade

User = get_user_model()

class OportunidadeCanalTest(APITestCase):
    def setUp(self):
        # 1. Criar Canal
        self.canal = Canal.objects.create(nome='Canal Vendas SP', slug='vendas-sp')
        
        # 2. Criar Usuário Vendedor vinculado ao Canal
        self.user = User.objects.create_user(
            username='vendedor_sp', 
            password='password123',
            perfil='VENDEDOR',
            canal=self.canal
        )
        self.client.force_authenticate(user=self.user)
        
        # 3. Criar Funil e Estágios
        self.funil = Funil.objects.create(nome='Funil Padrão', tipo='VENDAS')
        self.estagio_inicial = EstagioFunil.objects.create(nome='Prospecção', tipo='ABERTO')
        self.estagio_meio = EstagioFunil.objects.create(nome='Qualificação', tipo='ABERTO')
        
        # Vincular estágios ao funil e definir Prospecção como padrão
        FunilEstagio.objects.create(funil=self.funil, estagio=self.estagio_inicial, ordem=0, is_padrao=True)
        FunilEstagio.objects.create(funil=self.funil, estagio=self.estagio_meio, ordem=1, is_padrao=False)
        
        # Dar acesso ao usuário ao funil
        self.funil.usuarios.add(self.user)
        
        # 4. Criar uma Conta (Empresa) para associar à oportunidade
        self.conta = Conta.objects.create(nome_empresa='Empresa do Cliente', proprietario=self.user)

    def test_criacao_oportunidade_canal_automatico(self):
        """
        Cenário: Um vendedor logado cria uma oportunidade sem especificar o canal nem o estágio.
        Esperado: O sistema deve atribuir automaticamente o canal do usuário e o estágio padrão do funil.
        """
        data = {
            "nome": "Novo Negócio Estratégico",
            "funil": self.funil.id,
            "conta": self.conta.id,
            "valor_estimado": 5000.00
        }
        
        response = self.client.post('/api/oportunidades/', data, format='json')
        
        # Verificar se a requisição foi bem sucedida
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        
        # Buscar a oportunidade criada no banco
        oportunidade = Oportunidade.objects.get(id=response.data['id'])
        
        # Validações solicitadas pelo usuário:
        
        # 1. Canal Correto (Deve vir do usuário logado)
        self.assertEqual(oportunidade.canal.id, self.canal.id, "O canal deveria ter sido atribuído automaticamente a partir do usuário")
        
        # 2. Funil Correto (O que enviamos no POST)
        self.assertEqual(oportunidade.funil.id, self.funil.id, "O funil não corresponde ao enviado")
        
        # 3. Estágio Correto (Deve ser o padrão do funil, já que não enviamos no POST)
        self.assertEqual(oportunidade.estagio.id, self.estagio_inicial.id, "O estágio deveria ser o 'Prospecção' (padrão do funil)")
        
        # 4. Proprietário (Deve ser o usuário logado)
        self.assertEqual(oportunidade.proprietario.id, self.user.id)

    def test_criacao_oportunidade_estagio_especifico(self):
        """
        Cenário: Vendedor cria oportunidade já em um estágio avançado.
        Esperado: O sistema deve respeitar o estágio enviado, mas manter o canal automático.
        """
        data = {
            "nome": "Negócio em Qualificação",
            "funil": self.funil.id,
            "estagio": self.estagio_meio.id,
            "conta": self.conta.id
        }
        
        response = self.client.post('/api/oportunidades/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        oportunidade = Oportunidade.objects.get(id=response.data['id'])
        
        # Validar que respeitou o estágio enviado
        self.assertEqual(oportunidade.estagio.id, self.estagio_meio.id)
        # Validar que manteve o canal automático
        self.assertEqual(oportunidade.canal.id, self.canal.id)
