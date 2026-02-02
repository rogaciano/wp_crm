# Reestruturação do CRM - Plano de Implementação

## Resumo das Mudanças

A reestruturação visa **simplificar o fluxo** removendo a redundância entre Leads e Oportunidades, mantendo apenas **Oportunidades** como ponto central de negociação.

### Nova Hierarquia
```
Contato ←→ Empresa (Conta)
    ↓           ↓
    └─────→ Oportunidade ←─────┘
```

---

## Fase 1: Ajustes no Modelo de Contato ✅ COMPLETA

### Backend ✅
- [x] Adicionar campo `proprietario` (já existia)
- [x] Criar modelo `ContatoTelefone` (múltiplos telefones)
- [x] Criar modelo `ContatoEmail` (múltiplos emails)
- [x] Criar modelo `Tag` e relação N:N
- [x] Criar modelo `ContatoAnexo` (arquivos)
- [x] TagViewSet com endpoint `/api/tags/`
- [x] Atualizar serializers

### Frontend ✅
- [x] Atualizar `ContatoModal.vue`:
  - Lista dinâmica de telefones (+)
  - Lista dinâmica de emails (+)
  - Campo de tags (chips coloridos clicáveis)
  - Botão (+) Empresa (abre ContaModal)
- [x] Criar `ContatoDetailView.vue`:
  - Dados do contato
  - Empresa vinculada (clicável)
  - Redes sociais
  - Responsável
  - Notas
  - Botões Editar e WhatsApp
- [x] Atualizar `ContatosView.vue`:
  - Nome clicável → abre ficha

---

## Fase 2: Ajustes no Modelo de Empresa (Conta) ✅ COMPLETA

### Frontend ✅
- [x] Atualizar `ContaDetailView.vue`:
  - Botão (+) Contato (modal rápido) ✅
  - Lista de contatos vinculados com links para fichas ✅
  - Lista de oportunidades vinculadas com design rico ✅
  - Navegação entre Empresa e Contatos fluida ✅

---

## Fase 3: Reestruturar Oportunidades

### Backend
- [x] Adicionar relação N:N com Contatos (`oportunidade_contatos`)
- [x] Adicionar relação N:N com Empresas (`oportunidade_empresas`)
- [x] Mover diagnóstico de maturidade de Lead para Oportunidade
- [x] Criar modelo `OportunidadeAnexo`
- [x] Definir funil e estágio padrão na criação

### Frontend
- [x] Atualizar `OportunidadeModal.vue`:
  - [x] Autocomplete para buscar/vincular Contatos
  - [x] Botão (+) Criar Contato Rápido
  - [x] Autocomplete para buscar/vincular Empresas
  - [x] Botão (+) Criar Empresa Rápida
  - [x] Seção de anexos
- [x] Kanban: 
  - [x] Ao criar do Kanban, usar funil/estágio do contexto
  - [x] Mostrar contatos/empresas no card
- [x] Atualizar `ContatoDetailView.vue`:
  - [x] Mostrar oportunidades vinculadas corretamente

---

## Fase 4: Remover Leads ✅ COMPLETA
- [x] Remover rotas de Leads da API
- [x] Migrar dados de Leads para Oportunidades (Data Migration)
- [x] Remover modelo Lead do banco de dados (Schema Migration)
- [x] Remover `LeadModal.vue` e `LeadsView.vue`
- [x] Remover opção "Lead" do Kanban e Funis
- [x] Atualizar dashboard e contadores de mensagens

---

## Fase 5: Lista de Contatos Melhorada

### Frontend
- [x] `ContatosView.vue`:
  - [x] Coluna Nome (clicável → abre ficha)
  - [x] Coluna Empresa (clicável → abre ficha empresa)
  - [x] Coluna Oportunidades (contador)
  - [x] Coluna Tags
  - [x] Filtros por empresa, tags, responsável


## Fase 6: Timeline Unificada (Estilo KOMMO) ✅ COMPLETA

### Backend
- [x] Criar endpoint unificado `/api/timeline/`
  - Deve agregar: `Atividades` (Notas, Tarefas), `WhatsappMessage`, `Logs`
  - Ordenação cronológica decrescente
  - Paginação eficiente
- [x] Garantir que `WhatsappMessages` estejam vinculadas a Oportunidades/Contatos

### Frontend
- [x] Criar componente `TimelineFeed.vue`
- [x] Estilização visual distinta para cada tipo de item:
  - 📞 Ligação (ícone telefone)
  - 📝 Nota (fundo amarelo suave ou cinza)
  - 💬 WhatsApp (balões de chat verde/branco)
  - ✅ Tarefa (checkbox checkável)
- [x] Integrar em `OportunidadeModal` e `ContatoDetailView`


## Melhorias Futuras
- [ ] Histórico de atividades completo
- [ ] Timeline unificada
- [ ] Busca global entre contatos/empresas/oportunidades

---

## Ordem de Execução

1. ✅ **Fase 1** - Contatos (base para tudo)
2. 🔜 **Fase 2** - Empresas (conexão bidirecional)
3. ⏳ **Fase 3** - Oportunidades (ponto central)
4. ✅ **Fase 5** - Lista melhorada
5. ✅ **Fase 4** - Remover Leads (Fim do legado)

> ⚠️ **IMPORTANTE**: A Fase 4 deve ser a última para não quebrar funcionalidades existentes durante o desenvolvimento.
