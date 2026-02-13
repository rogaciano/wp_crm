from django.test import TestCase
from .models import Canal, Funil, EstagioFunil, Oportunidade, Conta, FunilEstagio
from django.contrib.auth import get_user_model

User = get_user_model()

class OportunidadeAutomationTest(TestCase):
    def setUp(self):
        # Criar Canal
        self.canal = Canal.objects.create(nome='Canal Teste', slug='teste')
        
        # Criar Usuário (importante: criar após o canal porque perfis precisam de canal)
        self.user = User.objects.create_user(
            username='testuser', 
            password='password',
            perfil='VENDEDOR',
            canal=self.canal
        )
        
        # Criar Conta
        self.conta = Conta.objects.create(nome_empresa='Empresa Teste', proprietario=self.user)
        
        # Configurar Funil de Vendas
        self.funil_vendas = Funil.objects.create(nome='Vendas', tipo=Funil.TIPO_VENDAS)
        self.estagio_aberto = EstagioFunil.objects.create(nome='Aberto', tipo=EstagioFunil.TIPO_ABERTO)
        self.estagio_ganho = EstagioFunil.objects.create(nome='Ganho', tipo=EstagioFunil.TIPO_GANHO)
        
        FunilEstagio.objects.create(funil=self.funil_vendas, estagio=self.estagio_aberto, ordem=0)
        FunilEstagio.objects.create(funil=self.funil_vendas, estagio=self.estagio_ganho, ordem=1)
        
        # Criar Oportunidade Inicial
        self.oportunidade = Oportunidade.objects.create(
            nome='Negócio Teste',
            conta=self.conta,
            funil=self.funil_vendas,
            estagio=self.estagio_aberto,
            proprietario=self.user,
            valor_estimado=1000,
            canal=self.canal
        )

    def test_automacao_pos_venda_suporte(self):
        """
        Testa se ao mudar para o estágio GANHO, as oportunidades de 
        Pós-Venda e Suporte são criadas automaticamente via signals.
        """
        # Mudar estágio para GANHO
        self.oportunidade.estagio = self.estagio_ganho
        self.oportunidade.save()
        
        # Verificar se as novas oportunidades foram criadas
        pos_venda = Oportunidade.objects.filter(
            conta=self.conta, 
            nome__icontains="Pós-Venda"
        ).first()
        
        suporte = Oportunidade.objects.filter(
            conta=self.conta, 
            nome__icontains="Suporte"
        ).first()
        
        self.assertIsNotNone(pos_venda, "Oportunidade de Pós-Venda não foi criada")
        self.assertIsNotNone(suporte, "Oportunidade de Suporte não foi criada")
        self.assertEqual(pos_venda.canal, self.canal)
        self.assertEqual(suporte.canal, self.canal)
