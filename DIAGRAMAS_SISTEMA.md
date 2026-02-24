# Diagramas do Sistema - CRM WP

Este documento contém o Diagrama de Fluxo de Dados (DFD) e o Diagrama de Entidade-Relacionamento (ERD) do projeto CRM WP.

## 1. Diagrama de Fluxo de Dados (DFD)

O DFD ilustra como as informações se movem através do sistema, desde as entradas externas até o armazenamento e as saídas.

### DFD Nível 0 (Diagrama de Contexto)
Mostra a visão geral do sistema e suas interações com entidades externas (usuários e integrações).

```mermaid
graph TD
    %% Entidades Externas
    U[Usuário / Vendedor]
    CLI[Cliente / Lead]
    WA[Evolution API / WhatsApp]
    
    %% Sistema Central
    CRM((Sistema\nCRM WP))
    
    %% Fluxos de Dados
    U -- "Credenciais, Cadastros, Movimentação no Kanban" --> CRM
    CRM -- "Painel de Vendas, Relatórios, Notificações" --> U
    
    CLI -- "Mensagens do WhatsApp" --> WA
    WA -- "Webhooks (Mensagens Recebidas)" --> CRM
    CRM -- "Requisições de Envio de Mensagens" --> WA
    WA -- "Mensagens Entregues" --> CLI
```

### DFD Nível 1 (Processos Principais)
Detalhamento dos principais processos internos, fluxos de dados e locais de armazenamento do sistema.

```mermaid
graph TD
    %% Entidades Externas
    U[Usuário]
    WA[Evolution API]
    
    %% Processos
    P1((1.0 Gestão de\nAutenticação))
    P2((2.0 Gestão de\nCadastros))
    P3((3.0 Gestão do\nFunil/Kanban))
    P4((4.0 Processamento\nde Mensagens))
    
    %% Armazenamento (Banco de Dados)
    D1[(D1: BD Usuários)]
    D2[(D2: BD Contatos/Contas)]
    D3[(D3: BD Oportunidades)]
    D4[(D4: BD Histórico WhatsApp)]
    
    %% Fluxos P1
    U -- "Login / Senha" --> P1
    P1 -- "Valida Credenciais" --> D1
    P1 -- "Token JWT" --> U
    
    %% Fluxos P2
    U -- "Dados do Lead/Cliente" --> P2
    P2 -- "Registra Conta/Contato" --> D2
    
    %% Fluxos P3
    U -- "Atualizações de Estágio" --> P3
    D2 -- "Lê Dados do Cliente" --> P3
    P3 -- "Salva Oportunidade" --> D3
    P3 -- "Painel Atualizado" --> U
    
    %% Fluxos P4
    WA -- "Payload Webhook" --> P4
    P4 -- "Grava Mensagem" --> D4
    P4 -- "Notifica Transcrição/Novo Áudio" --> U
    
    U -- "Texo/Áudio" --> P4
    P4 -- "Dispara POST" --> WA
```

---

## 2. Diagrama de Entidade-Relacionamento (ERD)

O ERD detalha a estrutura do banco de dados relacional e como as entidades do sistema se conectam.

```mermaid
erDiagram
    %% Hierarquia de Acesso
    CANAL ||--o{ USER : "possui vendedores"
    USER ||--o{ CONTA : "proprietário"
    USER ||--o{ CONTATO : "proprietário"
    USER ||--o{ OPORTUNIDADE : "proprietário"
    USER ||--o{ ATIVIDADE : "criador/atribuído"

    %% Relacionamentos Core
    CONTA ||--o{ CONTATO : "possui"
    CONTA ||--o{ OPORTUNIDADE : "possui"
    
    CONTATO ||--o{ OPORTUNIDADE : "contato principal"
    CONTATO ||--o{ WHATSAPP_MESSAGE : "possui mensagens"
    
    %% Funil e Estágios
    FUNIL ||--o{ ESTAGIO_FUNIL : "contém"
    FUNIL ||--o{ OPORTUNIDADE : "pertence ao"
    ESTAGIO_FUNIL ||--o{ OPORTUNIDADE : "está no"
    
    %% Atividades (Polimórficas)
    ATIVIDADE }o--|| CONTA : "referente a (Generic)"
    ATIVIDADE }o--|| CONTATO : "referente a (Generic)"
    ATIVIDADE }o--|| OPORTUNIDADE : "referente a (Generic)"
    
    %% Entidades Detalhadas
    USER {
        int id PK
        string username
        string email
        string perfil "ADMIN, RESPONSAVEL, VENDEDOR"
    }

    CANAL {
        int id PK
        string nome
        string evolution_instance
    }

    CONTA {
        int id PK
        string nome_empresa
        string cnpj
        string brand
    }

    CONTATO {
        int id PK
        string nome
        string telefone "Chave para o WhatsApp"
        string email
    }

    FUNIL {
        int id PK
        string nome
        string tipo
    }

    ESTAGIO_FUNIL {
        int id PK
        string nome
        string cor
        int ordem
    }

    OPORTUNIDADE {
        int id PK
        string nome
        decimal valor_estimado
        date data_fechamento_esperada
        string status "ABERTO, GANHO, PERDIDO"
        int estagio_id FK
        int proprietario_id FK
    }

    ATIVIDADE {
        int id PK
        string tipo "LIGAÇÃO, TAREFA, REUNIÃO"
        string status
        datetime data_vencimento
    }

    WHATSAPP_MESSAGE {
        int id PK
        string id_mensagem
        string texto
        string tipo "text, audio, image"
        datetime timestamp
    }
```

---

## 3. Fluxograma (Business Process / Pipeline de Vendas)

Mapeia as etapas lógicas de um vendedor dentro do sistema, desde a captação até o fechamento.

```mermaid
graph TD
    %% Atores
    V[Vendedor]
    S[Sistema CRM WP]
    
    %% Fluxo
    A[Login no CRM] --> B{Possui Leads \nNovos?}
    B -- Não --> C[Prospecção Ativa / \nAguardar Inbound]
    B -- Sim --> D[Acessar Oportunidade no Kanban]
    
    C --> D
    
    D --> E[Qualificação / \nContato (WhatsApp)]
    E --> F{Lead \nQualificado?}
    F -- Não --> G[Mover para 'Perdido']
    F -- Sim --> H[Levantamento de \nNecessidades / Reunião]
    
    H --> I[Apresentação de \nProposta / Cotação]
    I --> J{Proposta \nAceita?}
    J -- Não --> K[Negociação / \nRevisão da Proposta]
    K --> I
    J -- Sim --> L[Fechamento / \nMover para 'Ganho']
    
    L --> M[Faturamento / \nPassagem para Pós-Venda]
```

---

## 4. Diagrama de Estado (State Diagram)

Demonstra os diferentes status que uma **Oportunidade** pode ter e as transições no ciclo de vida.

```mermaid
stateDiagram-v2
    [*] --> ABERTO : Criação (Manual ou Via Integração)
    
    state ABERTO {
        [*] --> Contato_Inicial
        Contato_Inicial --> Qualificacao
        Qualificacao --> Apresentacao_Proposta
        Apresentacao_Proposta --> Negociacao
        Negociacao --> Aguardando_Assinatura
    }
    
    ABERTO --> GANHO : Fechamento Bem Sucedido
    ABERTO --> PERDIDO : Cliente Desistiu ou Desqualificado
    
    GANHO --> POS_VENDA : Transição Automática (Signal)
    PERDIDO --> Arquivado
    GANHO --> [*]
    Arquivado --> [*]
```

---

## 5. Mapa Mental (Mind Map)

Visão macro de toda a arquitetura de módulos e funcionalidades do CRM WP.

```mermaid
mindmap
  root((CRM WP))
    Vendas(Módulo de Vendas)
      Kanban[Funis de Vendas e Kanban]
      Oportunidades[Gestão de Oportunidades]
      Atividades(Tarefas e Reuniões)
    Contatos(Gestão de Cadastros)
      Contas(Empresas / B2B)
      Pessoas(Contatos Físicos)
    Comunicacao(Omnichannel)
      WhatsApp[Integração Evolution API]
      Audio(Transcrição de Áudios)
      Templates[Templates de Mensagens]
    Relatorios(Dashboards)
      Metricas[Métricas de Conversão]
      Atendimentos[Tempo de Resposta]
    Configuracoes(Administração)
      Usuarios [Gestão de Usuários/Vendedores]
      Canais[Gestão de Canais]
      Estagios(Personalização de Estágios)
```

---

## 6. Jornada do Usuário (User Journey)

Avalia a experiência e os passos de um **Vendedor** ao usar a aplicação, desde o login até o fechamento, medindo o nível de satisfação/complexidade (1 a 5).

```mermaid
journey
    title Jornada de Vendas - Vendedor (CRM WP)
    section Início do Dia
      Login no sistema: 5: Vendedor
      Visualizar Dashboard e Metas: 4: Vendedor
      Checar notificações (WhatsApp pendente): 5: Vendedor
    section Atendimento e Qualificação
      Responder novo lead no WhatsApp: 5: Vendedor
      Ouvir / Transcrever áudio recebido: 4: Vendedor
      Mover card no Kanban para 'Qualificação': 5: Vendedor
      Registrar notas e agendar reunião (Atividade): 3: Vendedor
    section Negociação e Fechamento
      Gerar proposta comercial: 3: Vendedor
      Enviar proposta via WhatsApp: 5: Vendedor
      Negociar valores / Ajustar proposta: 3: Vendedor
      Mover card para 'Aguardando Assinatura': 5: Vendedor
      Mover card para 'GANHO': 5: Vendedor
```
