"""
Script para verificar e testar o sistema de logs
Execute no servidor: python manage.py shell < test_logs.py
"""
import os
import django

# Configura Django (se necessário)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    django.setup()
except:
    pass  # Já configurado

from crm.models import Log, Contato, User

print("\n" + "="*60)
print("VERIFICAÇÃO DO SISTEMA DE LOGS")
print("="*60 + "\n")

# 1. Verifica se existem logs
total_logs = Log.objects.count()
print(f"1. Total de logs na tabela: {total_logs}")

# 2. Mostra os últimos 5 logs
if total_logs > 0:
    print("\n   Últimos 5 logs:")
    for log in Log.objects.order_by('-timestamp')[:5]:
        print(f"   - [{log.timestamp}] {log.acao} | {log.modelo} | {log.objeto_repr}")
else:
    print("\n   ⚠️  NENHUM LOG ENCONTRADO!")
    print("   Os logs começam a ser gravados quando ações são realizadas.")
    print("   Tente criar, editar ou excluir um contato para gerar logs.")

# 3. Verifica se signals estão carregados
print("\n2. Verificando se signals estão carregados...")
try:
    from crm import signals
    print("   ✓ Signals importados com sucesso!")
except Exception as e:
    print(f"   ✗ Erro ao importar signals: {e}")

# 4. Verifica se middleware está configurado
print("\n3. Verificando middleware...")
try:
    from django.conf import settings
    middlewares = settings.MIDDLEWARE
    has_middleware = any('CurrentUserMiddleware' in m for m in middlewares)
    if has_middleware:
        print("   ✓ CurrentUserMiddleware está configurado!")
    else:
        print("   ✗ CurrentUserMiddleware NÃO encontrado!")
except Exception as e:
    print(f"   ✗ Erro ao verificar middleware: {e}")

# 5. Cria um log de teste manual
print("\n4. Criando log de teste...")
try:
    admin = User.objects.filter(is_superuser=True).first()
    Log.objects.create(
        usuario=admin,
        acao='VIEW',
        modelo='Sistema',
        objeto_id=None,
        objeto_repr='Teste de log manual',
        observacao='Log criado via script de teste'
    )
    print("   ✓ Log de teste criado com sucesso!")
    
    # Verifica novamente
    novo_total = Log.objects.count()
    print(f"   Total de logs agora: {novo_total}")
except Exception as e:
    print(f"   ✗ Erro ao criar log de teste: {e}")

print("\n" + "="*60)
print("FIM DA VERIFICAÇÃO")
print("="*60 + "\n")
