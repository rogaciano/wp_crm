# CRM WP - Documentação da Estrutura do Projeto

## Visão Geral

Sistema de CRM (Customer Relationship Management) desenvolvido com Django + Vue.js, com integração WhatsApp via Evolution API. Implementa gestão completa de pipeline de vendas, ferramentas de diagnóstico empresarial, suporte multi-canal e rastreamento de atividades.

---

## 1. Estrutura de Diretórios

### Backend (Django)
```
backend/
├── config/                 # Configuração Django
│   ├── settings.py        # Configurações principais
│   ├── urls.py            # Rotas principais
│   └── wsgi.py            # Configuração WSGI
├── crm/                   # Aplicação principal
│   ├── models.py          # Modelos do banco de dados
│   ├── views.py           # ViewSets da API
│   ├── serializers.py     # Serializers DRF
│   ├── urls.py            # Rotas da API
│   ├── permissions.py     # Permissões customizadas
│   ├── middleware.py      # Middlewares
│   ├── migrations/        # Migrações do banco
│   └── services/          # Serviços de negócio
│       ├── ai_service.py          # Análise IA de diagnósticos
│       ├── evolution_api.py       # Integração WhatsApp
│       ├── audio_transcription.py # Transcrição de áudio
│       └── media_processor.py     # Processamento de mídia
└── manage.py
```

### Frontend (Vue.js)
```
frontend/src/
├── views/                 # Páginas
│   ├── DashboardView.vue
│   ├── KanbanView.vue
│   ├── ContasView.vue / ContaDetailView.vue
│   ├── ContatosView.vue / ContatoDetailView.vue
│   ├── OportunidadesView.vue / OportunidadeDetailView.vue
│   ├── AtividadesView.vue
│   ├── admin/             # Páginas administrativas
│   └── public/            # Páginas públicas (diagnóstico)
├── components/            # Componentes reutilizáveis
│   ├── *Modal.vue         # Modais de formulário
│   ├── WhatsappChat.vue   # Chat WhatsApp
│   └── TimelineFeed.vue   # Timeline de atividades
├── stores/                # Pinia (estado global)
│   ├── auth.js            # Autenticação
│   ├── oportunidades.js   # Oportunidades
│   └── whatsapp.js        # WhatsApp
├── services/              # Serviços de API
│   └── api.js             # Instância Axios com JWT
├── router/                # Vue Router
└── layouts/               # Layouts
```

---

## 2. Entidades (Modelos)

### 2.1 Usuários e Autorização

#### **User** (Usuário)
Estende AbstractUser do Django.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| perfil | CharField | VENDEDOR \| RESPONSAVEL \| ADMIN |
| canal | FK → Canal | Canal associado |
| telefone | CharField | Telefone do usuário |
| avatar | ImageField | Foto de perfil |

**Relacionamentos:**
- N:1 com Canal (vendedores)
- 1:N com Conta, Contato, Oportunidade, Atividade (proprietário)
- N:M com Funil (acesso a funis)

---

#### **Canal** (Canal de Vendas)
Representa uma equipe/unidade de vendas.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| nome | CharField | Nome do canal |
| slug | SlugField | Identificador URL |
| responsavel | OneToOne → User | Responsável pelo canal |
| funil_padrao | FK → Funil | Funil padrão |
| estagio_inicial | FK → EstagioFunil | Estágio inicial |
| evolution_instance_name | CharField | Instância WhatsApp |
| evolution_token | CharField | Token da API |
| evolution_is_connected | Boolean | Status conexão WhatsApp |
| evolution_phone_number | CharField | Número conectado |

**Relacionamentos:**
- 1:1 com User (responsável)
- 1:N com User, Conta, Contato, Oportunidade

---

#### **Origem** (Fonte de Leads)
Classifica a origem das oportunidades.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| nome | CharField | Nome da origem (Google, Indicação, etc) |
| ativo | Boolean | Se está ativa |

---

### 2.2 Contas e Contatos

#### **Conta** (Empresa/Cliente)
Representa uma empresa prospecto ou cliente.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| nome_empresa | CharField | Nome da empresa |
| marca | CharField | Marca principal |
| cnpj | CharField | CNPJ (único) |
| telefone_principal | CharField | Telefone |
| email | EmailField | E-mail |
| website | URLField | Site |
| setor | CharField | Setor/indústria |
| endereco, cidade, estado, cep | CharField | Endereço completo |
| canal | FK → Canal | Canal associado |
| proprietario | FK → User | Dono da conta |

**Relacionamentos:**
- N:1 com User (proprietário), Canal
- 1:N com Contato, ContaMarca, Oportunidade, DiagnosticoResultado
- N:M com Oportunidade (empresas)

---

#### **Contato** (Pessoa de Contato)
Pessoa física vinculada a uma empresa.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| nome | CharField | Nome completo |
| email | EmailField | E-mail principal |
| telefone | CharField | Telefone fixo |
| celular | CharField | Celular |
| cargo | CharField | Cargo |
| departamento | CharField | Departamento |
| chave_pix | CharField | Chave PIX |
| foto | ImageField | Foto do contato |
| tipo_contato | FK → TipoContato | Tipo de contato |
| conta | FK → Conta | Empresa associada |
| canal | FK → Canal | Canal |
| proprietario | FK → User | Dono do contato |

**Relacionamentos:**
- N:1 com Conta, Canal, User, TipoContato
- 1:N com ContatoTelefone, ContatoEmail, ContatoRedeSocial, ContatoAnexo
- N:M com Tag, Oportunidade

---

#### **ContatoTelefone** (Telefones do Contato)
| Campo | Tipo | Descrição |
|-------|------|-----------|
| contato | FK → Contato | Contato |
| numero | CharField | Número |
| tipo | CharField | CELULAR \| COMERCIAL \| RESIDENCIAL \| WHATSAPP \| OUTRO |
| principal | Boolean | Se é o principal |

---

#### **ContatoEmail** (E-mails do Contato)
| Campo | Tipo | Descrição |
|-------|------|-----------|
| contato | FK → Contato | Contato |
| email | EmailField | E-mail |
| tipo | CharField | PESSOAL \| COMERCIAL \| OUTRO |
| principal | Boolean | Se é o principal |

---

#### **Tag** (Etiqueta)
| Campo | Tipo | Descrição |
|-------|------|-----------|
| nome | CharField | Nome da tag |
| cor | CharField | Cor hexadecimal |

---

#### **TipoContato** (Tipo de Contato)
| Campo | Tipo | Descrição |
|-------|------|-----------|
| nome | CharField | Nome (Padrão, Indicador, Decisor) |
| emoji | CharField | Emoji para exibição |
| descricao | TextField | Descrição |

---

#### **TipoRedeSocial** (Tipos de Redes Sociais)
| Campo | Tipo | Descrição |
|-------|------|-----------|
| nome | CharField | Nome (LinkedIn, Instagram, etc) |
| icone | CharField | Classe do ícone |
| cor | CharField | Cor hexadecimal |
| url_base | CharField | URL base para perfis |
| placeholder | CharField | Placeholder do input |

---

#### **ContatoRedeSocial** (Redes Sociais do Contato)
| Campo | Tipo | Descrição |
|-------|------|-----------|
| contato | FK → Contato | Contato |
| tipo | FK → TipoRedeSocial | Tipo de rede |
| valor | CharField | Username/URL |

---

### 2.3 Pipeline de Vendas

#### **Funil** (Funil de Vendas)
| Campo | Tipo | Descrição |
|-------|------|-----------|
| nome | CharField | Nome do funil |
| tipo | CharField | OPORTUNIDADE |
| is_active | Boolean | Se está ativo |

**Relacionamentos:**
- N:M com User (usuários com acesso)
- N:M com EstagioFunil (via FunilEstagio)
- 1:N com Oportunidade

---

#### **EstagioFunil** (Definição de Estágio)
| Campo | Tipo | Descrição |
|-------|------|-----------|
| nome | CharField | Nome do estágio |
| tipo | CharField | ABERTO \| GANHO \| PERDIDO |
| cor | CharField | Cor hexadecimal |

---

#### **FunilEstagio** (Relação Funil-Estágio)
| Campo | Tipo | Descrição |
|-------|------|-----------|
| funil | FK → Funil | Funil |
| estagio | FK → EstagioFunil | Estágio |
| ordem | PositiveInt | Ordem no funil |
| is_padrao | Boolean | Se é o estágio inicial |

---

### 2.4 Oportunidades e Precificação

#### **Plano** (Plano de Serviço)
| Campo | Tipo | Descrição |
|-------|------|-----------|
| nome | CharField | Nome do plano |
| preco_mensal | DecimalField | Preço mensal |
| preco_anual | DecimalField | Preço anual |
| descricao | TextField | Descrição |
| recursos | JSONField | Lista de recursos inclusos |

---

#### **PlanoAdicional** (Serviços Adicionais)
| Campo | Tipo | Descrição |
|-------|------|-----------|
| nome | CharField | Nome do adicional |
| preco | DecimalField | Preço |
| unidade | CharField | Unidade (usuário, CNPJ, hora) |

---

#### **Oportunidade** (Negócio/Deal)
| Campo | Tipo | Descrição |
|-------|------|-----------|
| nome | CharField | Nome da oportunidade |
| valor_estimado | DecimalField | Valor estimado |
| data_fechamento_esperada | DateField | Previsão de fechamento |
| probabilidade | PositiveInt | Probabilidade (0-100%) |
| estagio | FK → EstagioFunil | Estágio atual |
| conta | FK → Conta | Conta principal (legado) |
| contato_principal | FK → Contato | Contato principal |
| proprietario | FK → User | Dono da oportunidade |
| funil | FK → Funil | Funil |
| canal | FK → Canal | Canal |
| plano | FK → Plano | Plano selecionado |
| origem | FK → Origem | Origem do lead |
| periodo_pagamento | CharField | MENSAL \| ANUAL |
| forma_pagamento | CharField | CARTAO_RECORRENTE \| BOLETO |
| cortesia | TextField | Descrição de cortesias |
| cupom_desconto | CharField | Cupom aplicado |
| indicador_comissao | FK → Contato | Indicador para comissão |
| motivo_perda | TextField | Motivo da perda |
| data_fechamento_real | DateField | Data real de fechamento |

**Relacionamentos:**
- N:1 com User, EstagioFunil, Conta, Contato, Funil, Canal, Plano, Origem
- N:M com Conta (empresas), Contato (contatos), PlanoAdicional (adicionais)
- 1:N com OportunidadeAnexo, DiagnosticoResultado, WhatsappMessage, HistoricoEstagio

---

#### **OportunidadeAdicional** (Adicionais da Oportunidade)
| Campo | Tipo | Descrição |
|-------|------|-----------|
| oportunidade | FK → Oportunidade | Oportunidade |
| adicional | FK → PlanoAdicional | Adicional |
| quantidade | PositiveInt | Quantidade |

---

### 2.5 Atividades

#### **Atividade** (Tarefa/Interação)
Modelo polimórfico - pode ser associado a Conta, Contato ou Oportunidade.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| tipo | CharField | TAREFA \| LIGACAO \| REUNIAO \| EMAIL \| NOTA |
| titulo | CharField | Título |
| descricao | TextField | Descrição |
| data_vencimento | DateTimeField | Data de vencimento |
| status | CharField | Pendente \| Concluída \| Cancelada |
| proprietario | FK → User | Responsável |
| content_type | FK → ContentType | Tipo da entidade associada |
| object_id | PositiveInt | ID da entidade |
| associado_a | GenericFK | Relação genérica |

---

### 2.6 Diagnóstico Empresarial

#### **DiagnosticoPilar** (Pilar do Diagnóstico)
| Campo | Tipo | Descrição |
|-------|------|-----------|
| nome | CharField | Nome do pilar |
| slug | SlugField | Identificador URL |
| descricao | TextField | Descrição |
| ordem | PositiveInt | Ordem de exibição |
| cor | CharField | Cor para gráficos |

---

#### **DiagnosticoPergunta** (Pergunta)
| Campo | Tipo | Descrição |
|-------|------|-----------|
| pilar | FK → DiagnosticoPilar | Pilar |
| texto | TextField | Texto da pergunta |
| ordem | PositiveInt | Ordem |
| ajuda | TextField | Texto de ajuda |

---

#### **DiagnosticoResposta** (Opção de Resposta)
| Campo | Tipo | Descrição |
|-------|------|-----------|
| pergunta | FK → DiagnosticoPergunta | Pergunta |
| texto | TextField | Texto da resposta |
| pontuacao | IntegerField | Pontuação (0-10) |
| feedback | TextField | Feedback específico |

---

#### **DiagnosticoResultado** (Resultado)
| Campo | Tipo | Descrição |
|-------|------|-----------|
| conta | FK → Conta | Conta (opcional) |
| oportunidade | FK → Oportunidade | Oportunidade (opcional) |
| data_conclusao | DateTimeField | Data da conclusão |
| respostas_detalhadas | JSONField | Respostas brutas |
| pontuacao_por_pilar | JSONField | Pontuação por pilar |
| analise_ia | TextField | Análise gerada por IA |

---

### 2.7 Comunicação

#### **WhatsappMessage** (Mensagem WhatsApp)
| Campo | Tipo | Descrição |
|-------|------|-----------|
| id_mensagem | CharField | ID da Evolution API |
| instancia | CharField | Nome da instância |
| oportunidade | FK → Oportunidade | Oportunidade (opcional) |
| de_mim | Boolean | Se foi enviada pelo CRM |
| numero_remetente | CharField | Remetente |
| numero_destinatario | CharField | Destinatário |
| texto | TextField | Conteúdo |
| tipo_mensagem | CharField | text, image, video, etc |
| url_media | URLField | URL da mídia |
| lida | Boolean | Se foi lida |
| timestamp | DateTimeField | Horário da mensagem |

---

### 2.8 Auditoria

#### **Log** (Log de Auditoria)
| Campo | Tipo | Descrição |
|-------|------|-----------|
| usuario | FK → User | Usuário que executou |
| acao | CharField | CREATE \| UPDATE \| DELETE \| VIEW \| LOGIN \| LOGOUT |
| modelo | CharField | Nome do modelo afetado |
| objeto_id | PositiveInt | ID do objeto |
| objeto_repr | CharField | Representação string |
| alteracoes | JSONField | Detalhes das mudanças |
| ip_address | GenericIPAddress | IP do usuário |
| user_agent | TextField | User agent |
| timestamp | DateTimeField | Momento da ação |

---

#### **HistoricoEstagio** (Histórico de Mudanças de Estágio)
| Campo | Tipo | Descrição |
|-------|------|-----------|
| oportunidade | FK → Oportunidade | Oportunidade |
| estagio_anterior | FK → EstagioFunil | Estágio anterior |
| estagio_novo | FK → EstagioFunil | Novo estágio |
| nome_estagio_anterior | CharField | Nome preservado |
| nome_estagio_novo | CharField | Nome preservado |
| usuario | FK → User | Quem alterou |
| data_mudanca | DateTimeField | Data da mudança |
| observacao | TextField | Observações |

---

## 3. Diagrama de Relacionamentos

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              USER                                        │
│  (perfil: ADMIN | RESPONSAVEL | VENDEDOR)                               │
└─────────────────────────────────────────────────────────────────────────┘
        │ 1:1 responsavel          │ N:1 vendedores
        ▼                          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              CANAL                                       │
│  (WhatsApp: evolution_instance, evolution_token, evolution_phone)       │
└─────────────────────────────────────────────────────────────────────────┘
        │                    │                    │
        │ 1:N               │ 1:N               │ 1:N
        ▼                    ▼                    ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐
│    CONTA     │    │   CONTATO    │    │    OPORTUNIDADE      │
│  (empresa)   │◄───┤   (pessoa)   │◄───┤  (negócio/deal)      │
└──────────────┘    └──────────────┘    └──────────────────────┘
        │ 1:N              │ 1:N                  │
        ▼                  ▼                      │
┌──────────────┐    ┌──────────────┐             │
│ ContaMarca   │    │ContatoTelefone│             │
└──────────────┘    │ContatoEmail  │             │
                    │ContatoRedeSoc│             │
                    └──────────────┘             │
                           │ N:M                 │
                           ▼                     │
                    ┌──────────────┐             │
                    │     TAG      │             │
                    └──────────────┘             │
                                                 │
        ┌────────────────────────────────────────┤
        │                                        │
        ▼                                        ▼
┌──────────────┐                        ┌──────────────┐
│    FUNIL     │◄───────────────────────┤EstagioFunil  │
│(pipeline)    │   N:M via FunilEstagio │  (estágio)   │
└──────────────┘                        └──────────────┘
                                                 │
                                                 │ N:1
                                                 ▼
                                        ┌──────────────┐
                                        │HistoricoEsta│
                                        │    gio      │
                                        └──────────────┘

┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│    PLANO     │───►│Oportunidade  │◄───│PlanoAdicional│
│  (produto)   │    │  Adicional   │    │  (upgrade)   │
└──────────────┘    └──────────────┘    └──────────────┘

┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   ORIGEM     │───►│OPORTUNIDADE  │◄───│WhatsappMsg   │
│(fonte lead)  │    │              │    │              │
└──────────────┘    └──────────────┘    └──────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                         ATIVIDADE (Polimórfica)                         │
│  Pode ser associada a: Conta | Contato | Oportunidade                   │
│  Tipos: TAREFA | LIGACAO | REUNIAO | EMAIL | NOTA                       │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                         DIAGNÓSTICO                                      │
│  DiagnosticoPilar → DiagnosticoPergunta → DiagnosticoResposta           │
│                              ↓                                           │
│                    DiagnosticoResultado → (Conta | Oportunidade)         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Endpoints da API

### Base URL: `/api/`

### Autenticação
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | /auth/login/ | Login JWT |
| POST | /auth/refresh/ | Refresh token |

### Recursos Principais
| Recurso | Endpoints | Ações Extras |
|---------|-----------|--------------|
| /canais/ | CRUD | conectar-whatsapp, whatsapp/status, whatsapp/qrcode |
| /usuarios/ | CRUD | me (usuário atual) |
| /origens/ | CRUD | - |
| /funis/ | CRUD | - |
| /contas/ | CRUD | - |
| /contatos/ | CRUD | - |
| /tipos-contato/ | CRUD | - |
| /tipos-rede-social/ | CRUD | - |
| /tags/ | CRUD | - |
| /estagios-funil/ | CRUD | - |
| /oportunidades/ | CRUD | close, move-stage |
| /oportunidade-anexos/ | CRUD | - |
| /atividades/ | CRUD | concluir |
| /planos/ | CRUD | - |
| /adicionais-plano/ | CRUD | - |
| /diagnosticos/ | CRUD | submit-public, generate-report |
| /whatsapp/ | CRUD | send-message, conversations |
| /logs/ | Read-only | - |
| /timeline/ | Read-only | - |
| /dashboard/ | Read-only | summary, opportunities-by-stage, revenue-forecast |
| /organograma/ | Read-only | hierarchy |

---

## 5. Sistema de Permissões

### Perfis de Usuário
| Perfil | Acesso |
|--------|--------|
| **ADMIN** | Acesso total ao sistema |
| **RESPONSAVEL** | Gerencia seu canal e equipe |
| **VENDEDOR** | Gerencia seus próprios registros |

### Hierarquia de Visibilidade
- **Vendedor**: Vê apenas seus registros
- **Responsável**: Vê registros do seu canal
- **Admin**: Vê todos os registros

---

## 6. Tecnologias Utilizadas

### Backend
- Django 4.x
- Django REST Framework
- drf-spectacular (OpenAPI)
- Django Simple JWT
- MySQL/PostgreSQL

### Frontend
- Vue 3
- Vue Router
- Pinia (estado)
- Axios
- Tailwind CSS

### Integrações
- Evolution API (WhatsApp)
- LLM/IA (diagnósticos)

---

## 7. Estatísticas do Projeto

| Métrica | Valor |
|---------|-------|
| Total de Modelos | 32 |
| Views/Páginas Frontend | 24 |
| Componentes Modal | 14 |
| Endpoints API | 40+ |
| Stores Pinia | 3 |

---

*Documentação gerada em: 03/02/2026*
