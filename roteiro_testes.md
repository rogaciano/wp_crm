# Roteiro de Testes e Demonstração - CRM WP

Este documento descreve os principais cenários de teste para validar e demonstrar as funcionalidades críticas do CRM.

---

## Cenário 1: O Funil de Entrada (Lead Externo)
**Objetivo**: Demonstrar a captura automática de leads via canal público.

1.  **Ação**: Acessar a URL do Diagnóstico Público (ex: `/diagnostico-publico/matriz`).
2.  **Ação**: Preencher o formulário com dados fictícios de empresa (CNPJ real para testar o proxy da ReceitaWS) e contato.
3.  **Ação**: Responder as perguntas do diagnóstico até o final e submeter.
4.  **Resultado Esperado**:
    *   O sistema deve redirecionar para uma página de sucesso/resultado.
    *   No Backend/Admin, uma nova **Conta**, um **Contato** e uma **Oportunidade** devem ter sido criados automaticamente.
    *   A Oportunidade deve estar vinculada ao canal correto e no estágio inicial.

---

## Cenário 2: Gestão de Vendas (O Kanban)
**Objetivo**: Validar a movimentação de negócios e histórico.

1.  **Ação**: Abrir a `KanbanView.vue` e localizar a oportunidade criada no Cenário 1.
2.  **Ação**: Arrastar a oportunidade entre colunas (estágios).
3.  **Ação**: Entrar no detalhe da oportunidade e verificar o "Histórico de Estágios".
4.  **Resultado Esperado**:
    *   A movimentação deve ser persistida no banco em tempo real.
    *   O histórico deve registrar as datas e os estágios por onde a oportunidade passou.

---

## Cenário 3: Automação de "Ganho" (Pós-Venda e Suporte)
**Objetivo**: Testar a inteligência de fluxo de trabalho.

1.  **Ação**: No detalhe da oportunidade, alterar o status para o estágio configurado como **GANHO**.
2.  **Ação**: Verificar a lista de oportunidades globais ou o Kanban de outros funis.
3.  **Resultado Esperado**:
    *   O sistema deve capturar o sinal (`signals.py`) e criar automaticamente:
        *   Uma nova Oportunidade no funil de **Pós-Venda**.
        *   Uma nova Oportunidade no funil de **Suporte**.
    *   Ambas devem estar vinculadas à mesma Conta do cliente.

---

## Cenário 4: Comunicação Omnichannel (WhatsApp)
**Objetivo**: Demonstrar a integração com a Evolution API e IA.

1.  **Ação**: Abrir o detalhe de uma oportunidade que possua um contato com telefone celular.
2.  **Ação**: Enviar uma mensagem de texto pela interface do chat.
3.  **Ação (Simulação)**: Enviar um áudio do celular para o número conectado ao CRM.
4.  **Ação**: Clicar no botão "Transcrever" no balão de áudio recebido.
5.  **Resultado Esperado**:
    *   A mensagem enviada pelo CRM deve chegar no WhatsApp do cliente.
    *   O áudio recebido deve aparecer no chat e a transcrição via Faster-Whisper deve ser exibida ao clicar.

---

## Cenário 5: Auditoria e Segurança
**Objetivo**: Validar a rastreabilidade das ações.

1.  **Ação**: Logar com um usuário Admin e um usuário Vendedor.
2.  **Ação**: O Vendedor altera o valor estimado de uma oportunidade.
3.  **Ação**: O Admin acessa o painel de Logs de Auditoria.
4.  **Resultado Esperado**:
    *   Deve existir um registro detalhando: "Valor Estimado alterado de X para Y por Usuário Z".
    *   O Vendedor comum não deve conseguir visualizar oportunidades de outros vendedores (se configurado na hierarquia).

---

## Cenário 6: Produtividade (Atividades)
**Objetivo**: Testar a gestão de tarefas vinculadas.

1.  **Ação**: Criar uma nova "Atividade" do tipo "Ligação" com data de vencimento para hoje.
2.  **Ação**: Visualizar o Dashboard principal.
3.  **Ação**: Marcar a atividade como concluída.
4.  **Resultado Esperado**:
    *   O Dashboard deve exibir o alerta de atividade pendente.
    *   A atividade deve aparecer na timeline da Oportunidade/Contato relacionada.
    *   Após concluir, o contador de pendências no Dashboard deve atualizar.
