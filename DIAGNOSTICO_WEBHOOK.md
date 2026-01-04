# Diagnóstico do Problema de Webhook WhatsApp

## Problema Identificado
As mensagens enviadas pelo CRM não estão aparecendo no histórico.

## Causas Prováveis

### 1. O webhook não processa eventos SEND_MESSAGE
**Status**: ✅ CORRIGIDO

O código do webhook só processava eventos `MESSAGES_UPSERT`, mas não processava `SEND_MESSAGE`.

**Correção aplicada**: O webhook agora aceita os seguintes eventos:
- `messages.upsert` / `messages_upsert` (mensagens recebidas)
- `send_message` (mensagens enviadas)
- `messages.update` / `messages_update` (atualizações de mensagem)

### 2. Extração incorreta do ID da mensagem
**Status**: ✅ MELHORADO

O código agora tenta extrair o ID da mensagem em múltiplos formatos possíveis.

### 3. IDs locais vs IDs da Evolution API
**Status**: ⚠️ NECESSITA VERIFICAÇÃO

Quando você envia uma mensagem:
1. O endpoint `/whatsapp/send/` envia via Evolution API
2. Tenta extrair o ID da resposta
3. Se não conseguir, gera um ID local (`local_xxxxxx`)
4. Salva no banco com esse ID

O webhook TAMBÉM pode receber a mesma mensagem:
1. Evolution API envia notificação SEND_MESSAGE
2. Webhook tenta salvar com o ID real da Evolution
3. Se o ID for diferente, pode criar duplicata ou mensagem órfã

## Como Diagnosticar

### Passo 1: Verificar logs do servidor Django
```bash
# No servidor de produção
tail -f /var/www/wp_crm/backend/logs/app.log

# Ou se estiver usando stderr
journalctl -u gunicorn -f
```

Envie uma mensagem pelo CRM e observe:
- `[SEND] Estrutura da resposta: [...]` - mostra quais campos a Evolution retornou
- `[SEND] ID extraído: ...` - mostra o ID que foi extraído (ou None)
- `[WEBHOOK] Event: send_message` - confirma se o webhook recebeu o evento

### Passo 2: Verificar mensagens no banco de dados
```bash
cd /var/www/wp_crm/backend
source .venv/bin/activate
python manage.py shell
```

```python
from crm.models import WhatsappMessage

# Últimas 10 mensagens enviadas (de_mim=True)
msgs = WhatsappMessage.objects.filter(de_mim=True).order_by('-timestamp')[:10]
for msg in msgs:
    print(f"ID: {msg.id} | id_mensagem: {msg.id_mensagem} | texto: {msg.texto[:30]}... | timestamp: {msg.timestamp}")

# Verificar se há IDs locais
local_msgs = WhatsappMessage.objects.filter(id_mensagem__startswith='local_')
print(f"\nMensagens com ID local: {local_msgs.count()}")
for msg in local_msgs[:5]:
    print(f"  {msg.id_mensagem} - {msg.texto[:30]}...")
```

### Passo 3: Testar o webhook manualmente
```bash
# No servidor de desenvolvimento
cd /var/www/wp_crm/backend
python test_webhook_send_message.py
```

### Passo 4: Verificar configuração do webhook na Evolution API
```bash
cd /var/www/wp_crm/backend
python check_evolution.py
```

Confirme que:
- Webhook está habilitado: `Enabled: True`
- URL está correta: `https://crm.sistema9.com.br/api/webhooks/whatsapp/`
- Evento SEND_MESSAGE está na lista de eventos

## Possíveis Soluções

### Solução 1: Aguardar webhook em vez de salvar imediatamente
Modificar o endpoint `/whatsapp/send/` para NÃO salvar a mensagem imediatamente, apenas enviar via Evolution API. O webhook salvará quando receber o evento SEND_MESSAGE.

**Prós**:
- Evita duplicatas
- Garante ID consistente da Evolution

**Contras**:
- Pequeno delay até a mensagem aparecer (aguarda webhook)
- Se o webhook falhar, a mensagem não aparece no histórico

### Solução 2: Atualizar mensagem existente se webhook enviar
Manter o salvamento imediato, mas se o webhook receber a mesma mensagem com ID diferente, atualizar a existente em vez de criar nova.

**Implementação**:
```python
# No webhook, em vez de apenas verificar id_mensagem, verificar também:
# - Mesmo timestamp (±5 segundos)
# - Mesmo número destinatário
# - Mesmo texto (ou início do texto)
# Se encontrar, atualiza o id_mensagem em vez de criar nova
```

### Solução 3: Melhorar extração do ID (IMPLEMENTADA)
A correção aplicada melhora a extração do ID em vários formatos. Monitore os logs para ver se está funcionando.

## Logs para Monitorar

Após as correções aplicadas, quando você enviar uma mensagem, deve ver nos logs:

```
[SEND] Tentando enviar para 5581999216560 via https://evo.matutec.com.br
[SEND] Sucesso na API: {... resposta da Evolution ...}
[SEND] Estrutura da resposta: ['key', 'message', 'timestamp', ...]
[SEND] ID extraído: 3EB0ABCDEF123456
[WEBHOOK] Event: send_message, Instance: informsistemas
[WEBHOOK] Processando 1 mensagens do evento 'send_message'
[WEBHOOK] Estrutura da mensagem: ['key', 'message', 'messageTimestamp']
[WEBHOOK] Mensagem 3EB0ABCDEF... já existe (ID: 123), ignorando
```

Se o ID for `local_xxxxx`, significa que a Evolution não retornou o ID no formato esperado.

## Próximos Passos

1. ✅ Aplicar correções no webhook (FEITO)
2. 🔄 Fazer deploy das alterações
3. 🔄 Monitorar logs ao enviar mensagem
4. 🔄 Verificar se mensagens aparecem no histórico
5. 🔄 Se ainda houver problemas, implementar Solução 2

## Arquivos Modificados

- [backend/crm/views.py](backend/crm/views.py) - Linhas 1278-1320 (webhook) e 1109-1137 (send endpoint)
- [backend/test_webhook_send_message.py](backend/test_webhook_send_message.py) - Novo arquivo de teste
