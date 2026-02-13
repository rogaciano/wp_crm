# Documentação de Requisitos e Funcionalidades - CRM WP

Esta documentação descreve as principais funcionalidades, requisitos e processos de negócio implementados no sistema CRM WP.

---

## 1. Visão Geral
O **CRM WP** é uma plataforma de gestão de relacionamento com o cliente focada em otimizar o fluxo de vendas e centralizar a comunicação via WhatsApp. O sistema utiliza uma arquitetura moderna para garantir agilidade no atendimento e automação de processos comerciais.

---

## 2. Requisitos Funcionais (Principais Módulos)

### 2.1. Gestão de Oportunidades (Pipeline de Vendas)
*   **Kanban Multi-Funil**: Visualização das oportunidades em colunas de estágios. Suporte a diferentes tipos de funis (Vendas, Pós-Venda, Suporte).
*   **Gestão de Oportunidades**: Criação, edição e acompanhamento de negócios, incluindo valor estimado, data de fechamento e status (Aberto, Ganho, Perdido).
*   **Histórico de Estágios**: Registro automático de cada transição de etapa para análise de métricas de conversão.

### 2.2. Integração WhatsApp (Evolution API)
*   **Chat Centralizado**: Envio e recebimento de mensagens e mídias diretamente pelo CRM.
*   **Sincronização em Tempo Real**: Captura automática do histórico de conversas via Webhooks.
*   **Transcrição de Áudio**: Conversão automática de mensagens de voz em texto utilizando IA (Faster-Whisper).
*   **Gestão de Instâncias**: Suporte a múltiplos números/canais com painel de conexão (QR Code) integrado.

### 2.3. Sistema de Diagnóstico de Maturidade
*   **Captura de Leads (Formulário Público)**: Página pública para que clientes respondam um diagnóstico estratégico.
*   **Processamento Inteligente**: Geração automática de análise estratégica via IA baseada nas respostas.
*   **Geração Automática de Negócio**: Ao finalizar o diagnóstico, o sistema cria automaticamente o Contato, a Conta e uma Oportunidade no funil correspondente.

### 2.4. Gestão de Contas e Contatos
*   **Empresas (Contas)**: Centralização de dados corporativos, incluindo busca automática de dados via CNPJ (ReceitaWS).
*   **Pessoas (Contatos)**: Gestão de múltiplos contatos por empresa, com suporte a diversas redes sociais, telefones e e-mails.
*   **Tags e Categorização**: Classificação de contatos para segmentação.

### 2.5. Atividades e Produtividade
*   **Agendamento de Tarefas**: Gestão de ligações, reuniões, e-mails e notas vinculadas a oportunidades.
*   **Dashboard de Indicadores**: Resumo de vendas, atividades pendentes e mensagens não lidas.
*   **Notificações**: Alertas visuais de novas mensagens de WhatsApp e tarefas atrasadas.

---

## 3. Automações e Regras de Negócio

*   **Fluxo de Ganho de Negócio**: Ao marcar uma oportunidade como **GANHA**, o sistema cria automaticamente duas novas oportunidades:
    1.  Uma no funil de **Pós-Venda** (para Onboarding).
    2.  Uma no funil de **Suporte** (para acompanhamento técnico).
*   **Log de Auditoria**: Registro detalhado de quem alterou o quê e quando em todos os módulos críticos (Conta, Contato, Oportunidade).
*   **Hierarquia de Acesso**: Permissões baseadas em perfil (Admin, Vendedor, Responsável), onde vendedores acessam apenas seus leads e admins têm visão global.

---

## 4. Requisitos Não Funcionais
*   **Interface Responsiva**: Design otimizado para Desktop e Mobile, com suporte nativo a **Dark Mode**.
*   **Segurança**: Autenticação via JWT, proteção de rotas e validação de dados no backend.
*   **Escalabilidade**: Estrutura preparada para lidar com múltiplos usuários e alto volume de mensagens WhatsApp.

---

## 5. Pilha Tecnológica
*   **Backend**: Python / Django REST Framework.
*   **Frontend**: Javascript / Vue.js 3 / Vite.
*   **Banco de Dados**: MySQL.
*   **Serviços Externos**:
    *   Evolution API (WhatsApp).
    *   OpenAI / Faster-Whisper (IA e Transcrição).
    *   ReceitaWS (Consulta CNPJ).
