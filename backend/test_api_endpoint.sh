#!/bin/bash
# Script para testar o endpoint da API de mensagens
# Execute com: bash test_api_endpoint.sh

echo "=========================================="
echo "TESTANDO ENDPOINT /api/whatsapp/"
echo "=========================================="

# URL da API (ajuste se necessário)
API_URL="https://crm.sistema9.com.br/api/whatsapp/"

# Número para testar (Rogaciano)
NUMBER="5581999216560"

echo ""
echo "1. Testando sem autenticação (deve retornar 401 ou 403):"
echo "GET $API_URL?number=$NUMBER"
curl -s -w "\nStatus: %{http_code}\n" "$API_URL?number=$NUMBER" | head -20

echo ""
echo "=========================================="
echo "2. Testando COM autenticação:"
echo "=========================================="
echo ""
echo "Por favor, faça login no CRM e copie o token JWT."
echo "Depois execute:"
echo ""
echo "export TOKEN='seu_token_aqui'"
echo "curl -H \"Authorization: Bearer \$TOKEN\" \"$API_URL?number=$NUMBER\""
echo ""
echo "Ou use o navegador (F12 > Network > Headers) para ver a resposta"
