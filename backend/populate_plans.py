
import os
import django
import pymysql

# Configurar pymysql como substituto do mysqlclient
pymysql.install_as_MySQLdb()

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()

from crm.models import Plano, PlanoAdicional

plans = [
    {
        'nome': 'DAPIC LIGHT',
        'preco_mensal': 399.00,
        'preco_anual': 3990.00,
        'recursos': [
            'Suporte on-line',
            'Múltiplos estoques',
            'Curva ABC (produtos e clientes)',
            'Controle de ficha técnica e previsão de consumo',
            'Banco de dados ilimitado',
            '1 CNPJ incluso',
            '1 Usuário',
            'Videoaulas de treinamento gravadas'
        ]
    },
    {
        'nome': 'DAPIC STARTER',
        'preco_mensal': 499.00,
        'preco_anual': 4990.00,
        'recursos': [
            'Suporte on-line',
            'Múltiplos estoques',
            'Curva ABC (produtos e clientes)',
            'Controle de ficha técnica e previsão de consumo',
            'Banco de dados ilimitado',
            '1 CNPJ incluso',
            '5 Usuários',
            'Videoaulas de treinamento gravadas'
        ]
    },
    {
        'nome': 'DAPIC PREMIUM',
        'preco_mensal': 699.00,
        'preco_anual': 6990.00,
        'recursos': [
            'Suporte on-line',
            'Múltiplos estoques',
            'Curva ABC (produtos e clientes)',
            'Controle de ficha técnica e previsão de consumo',
            'Banco de dados ilimitado',
            '1 CNPJ incluso',
            '7 Usuários',
            '1 Integração com outra plataforma',
            'Relatórios B.I (Business Intelligence)',
            'Masterclass'
        ]
    },
    {
        'nome': 'DAPIC ADVANCED',
        'preco_mensal': 1099.00,
        'preco_anual': 10990.00,
        'recursos': [
            'Suporte on-line',
            'Múltiplos estoques',
            'Curva ABC (produtos e clientes)',
            'Controle de ficha técnica e previsão de consumo',
            'Banco de dados ilimitado',
            '2 CNPJs inclusos',
            '10 Usuários',
            '1 Integração com outra plataforma',
            'Relatórios B.I (Business Intelligence)',
            '2 horas de consultoria + Masterclass'
        ]
    }
]

for p_data in plans:
    plano, created = Plano.objects.update_or_create(
        nome=p_data['nome'],
        defaults=p_data
    )
    print(f"Plano {plano.nome} {'criado' if created else 'atualizado'}.")

# Adicionais
add_ons = [
    {'nome': 'Usuário adicional', 'preco': 35.00, 'unidade': 'usuário'},
    {'nome': 'Usuário representante', 'preco': 35.00, 'unidade': 'usuário'},
    {'nome': 'CNPJ adicional', 'preco': 399.00, 'unidade': 'CNPJ'},
    {'nome': 'Integração adicional', 'preco': 90.00, 'unidade': 'integração'},
    {'nome': 'Integração com Bling', 'preco': 110.00, 'unidade': 'integração'},
    {'nome': 'API', 'preco': 90.00, 'unidade': 'API'},
    {'nome': 'Módulo de B.I', 'preco': 120.00, 'unidade': 'mês'},
    {'nome': 'Consultoria remota', 'preco': 200.00, 'unidade': 'hora'},
    {'nome': 'Etiqueta personalizada', 'preco': 200.00, 'unidade': 'etiqueta'},
]

for add_data in add_ons:
    add, created = PlanoAdicional.objects.update_or_create(
        nome=add_data['nome'],
        defaults=add_data
    )
    print(f"Adicional {add.nome} {'criado' if created else 'atualizado'}.")
