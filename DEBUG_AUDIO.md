# Debug Áudio - Histórico de Correções

## Problema
Áudios do WhatsApp não reproduzem ("Ouvir") e não transcrevem ("Transcrever") no CRM.
Erro no frontend: "Não foi possível baixar o áudio do servidor. Verifique sua conexão."

## Causa Raiz Identificada
O `media_base64` dos áudios NÃO era salvo no banco de dados. Cada tentativa de ouvir/transcrever
dependia de baixar novamente da Evolution API via `getBase64FromMediaMessage`, que frequentemente
falhava (mídia expirada, timeout, etc).

---

## Correções Implementadas

### 1. `views.py` — Webhook descartava base64 de áudio (CRÍTICO)
**Linha ~2614:** Ao criar `WhatsappMessage`, o `media_base64` era salvo apenas para imagens.
```python
# ANTES (bug):
media_base64=media_base64 if mtype == 'image' else None,
# DEPOIS (fix):
media_base64=media_base64 if mtype in ['image', 'audio'] else None,
```

### 2. `evolution_api.py` — Bug de precedência Python (CRÍTICO)
**Método `get_media_base64`:** O operador ternário `if/else` se aplicava à expressão inteira,
retornando `None` mesmo quando `data['base64']` existia.
```python
# ANTES (bug - o if/else se aplica a TODA a cadeia or):
base64_data = (
    data.get('base64') or
    data.get('audio') or
    data.get('media') or
    data.get('data', {}).get('base64') if isinstance(data.get('data'), dict) else None
)
# DEPOIS (fix - parênteses isolam o último fallback):
base64_data = (
    data.get('base64') or
    data.get('audio') or
    data.get('media') or
    (data.get('data', {}).get('base64') if isinstance(data.get('data'), dict) else None)
)
```

### 3. `views.py` — Cache DB em `get_audio` e `transcribe_audio`
- Verificar `msg.media_base64` antes de baixar da Evolution API
- Salvar `media_base64` no banco após download bem-sucedido

### 4. `views.py` — Cache DB em `process_pending_media`
- Salvar `media_base64` junto com a transcrição

### 5. `media_processor.py` — Cache DB em `process_audio_async`
- Salvar `media_base64` junto com a transcrição no processamento assíncrono

### 6. `configure_webhook.py` — webhook_base64 estava False
- Alterado para `True` para que a Evolution API envie base64 inline no webhook
- Reescrito para buscar instâncias do banco (Canal) em vez do .env
- Formato do payload corrigido (camelCase + `enabled: true` + aninhado em `webhook`)

### 7. `.env` — EVOLUTION_INSTANCE_ID incorreto
- O `.env` tinha `informsistemas`, mas as instâncias reais estão no banco (Canal model)
- Não é mais usado para webhook config (script lê do banco agora)

---

## Configuração Evolution API

### Instâncias no banco (tabela Canal):
- `canal_pernambuco` (Pernambuco) ✅ Webhook configurado com webhook_base64=true
- `canal_bras_lia` (Brasília)
- `canal_fortaleza` (Fortaleza)
- `canal_goiania` (Goiania) — ⚠️ Não existe na Evolution API
- `canal_para_ba` (Paraíba) — ⚠️ Não existe na Evolution API
- `canal_rio_preto` (Rio Preto) — ⚠️ Não existe na Evolution API

### Endpoint webhook/set requer:
```json
{
    "webhook": {
        "enabled": true,
        "url": "https://crm.sistema9.com.br/api/webhooks/whatsapp/",
        "webhookByEvents": false,
        "webhookBase64": true,
        "events": ["MESSAGES_UPSERT", "MESSAGES_UPDATE"]
    }
}
```

---

## Status Atual (27/02/2026)
- ❌ Áudio AINDA não funciona após todas as correções
- ✅ Webhook configurado com webhook_base64=true para canal_pernambuco
- ✅ Gunicorn reiniciado
- ⚠️ PENDENTE: Verificar se git pull no servidor realmente trouxe views.py e evolution_api.py
- ⚠️ PENDENTE: Verificar logs do gunicorn para ver o erro real quando "Ouvir" é clicado

## Próximos Passos
1. Verificar no servidor: `grep -n "mtype in \['image', 'audio'\]" crm/views.py`
2. Verificar no servidor: `grep -n "data.get('data'" crm/services/evolution_api.py`
3. Verificar logs: `sudo journalctl -u gunicorn --since "10 min ago" | grep -i audio`
4. Se o código está OK, verificar se o webhook da Evolution API realmente envia base64
5. Testar endpoint get_audio direto: `curl -X POST .../api/whatsapp/get_audio/`
