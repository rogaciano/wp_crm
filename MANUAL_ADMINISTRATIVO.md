# 🛡️ Manual Administrativo - CRM de Vendas

Este manual destina-se aos usuários com perfil **ADMIN**, fornecendo instruções detalhadas sobre a configuração e gestão estratégica do sistema.

---

## 📑 Sumário
1. [Dashboard Executivo](#1-dashboard-executivo)
2. [Gestão de Usuários e Permissões](#2-gestão-de-usuários-e-permissões)
3. [Gestão de Canais de Venda](#3-gestão-de-canais-de-venda)
4. [Configuração do Funil (Estágios)](#4-configuração-do-funil-estágios)
5. [Planos, Preços e Adicionais](#5-planos-preços-e-adicionais)

---

## 1. Dashboard Executivo
O Dashboard é a central de inteligência do sistema, consolidando dados de todos os canais e vendedores.

*   **KPIs Principais:**
    *   **Receita Ganha:** Valor total de oportunidades marcadas como "Ganho" no período selecionado.
    *   **Pipeline Ativo:** Soma do valor de todas as oportunidades atualmente em estágios "Abertos".
    *   **Win Rate:** Percentual de conversão (Vendas Ganhas / Total de Vendas Fechadas).
    *   **Ticket Médio:** Valor médio por venda realizada.
    *   **Novos Leads:** Volume de prospecção no período.
*   **Filtros de Período:** Use os botões (7D, 30D, 90D, 1 Ano) para ajustar a janela temporal dos dados.
*   **Gráficos:**
    *   **Pipeline por Estágio:** Visualização do volume financeiro em cada etapa do funil.
    *   **Maturidade dos Leads:** Média dos resultados dos diagnósticos realizados.
    *   **Performance Mensal:** Tendência de crescimento de novas oportunidades vs. vendas ganhas.

---

## 2. Gestão de Usuários e Permissões
Localizado em `Admin > Usuários`, este módulo controla quem acessa o sistema e o que pode ver.

*   **Perfis de Acesso:**
    *   **Administrador:** Acesso global. Vê dados de todos os canais e tem acesso ao menu Admin.
    *   **Responsável:** Gestor de um canal. Vê os leads, contas e vendas de todos os vendedores vinculados ao seu canal.
    *   **Vendedor:** Operacional. Vê apenas os seus próprios registros.
*   **Vínculo com Canal:** 
    *   Ao cadastrar um usuário, você deve vinculá-lo a um **Canal de Venda**. 
    *   Este canal funcionará como a sua "unidade/região" padrão. Isso automatiza o faturamento: quando este vendedor criar uma venda, o canal dele virá pré-selecionado, garantindo o direcionamento correto do suporte e comissões.
*   **Ativação/Desativação:** Utilize o botão de status para bloquear imediatamente o acesso de usuários desligados, mantendo o histórico de dados intacto.

---

## 3. Gestão de Canais de Venda
Canais representam suas unidades de negócio, parceiros ou filiais.

*   **Cadastro:** Defina o nome do canal (ex: "Matriz", "Pernambuco", "Canal Norte").
*   **Suporte e Faturamento:** O sistema agora utiliza os Canais como os centros de suporte. No momento do fechamento da venda (Modal de Faturamento), o administrador ou vendedor pode selecionar qual Canal será responsável por aquela conta.
*   **Hierarquia:** Cada Lead ou Conta no sistema é "carimbado" com o canal do vendedor que o criou. Isso garante que o Responsável do Canal consiga gerir sua equipe de forma isolada de outros canais.

---

## 4. Configuração do Funil (Estágios)
O funil de vendas é totalmente customizável para se adaptar ao seu processo comercial.

*   **Ordem:** Define a sequência em que as colunas aparecem no **Kanban**.
*   **Tipos de Estágio:**
    *   **Aberto:** Oportunidades em negociação.
    *   **Ganho:** Negócio fechado (alimenta a Receita Ganha).
    *   **Perdido:** Negócio cancelado.
*   **Cores:** Utilize cores para identificar visualmente a temperatura do negócio no Kanban (ex: azul para início, verde para fechamento).

---

## 5. Planos, Preços e Adicionais
Configuração crucial para a geração automática do **Texto de Faturamento**.

*   **Planos (DAPIC):** Cadastre os produtos principais com seus respectivos valores para pagamento **Mensal** e **Anual**.
*   **Recursos Adicionais:** Cadastre itens extras (ex: usuários adicionais, módulos extras) que possuem custo específico.
*   **Faturamento:** No modal de faturamento de uma oportunidade, ao selecionar um plano e seus adicionais, o sistema calcula automaticamente o VR (Valor Recorrente) e gera um texto padrão para ser enviado ao financeiro/cliente.

---

## 🔐 Segurança e Boas Práticas
*   Nunca compartilhe senhas de administrador.
*   Ao criar novos usuários, forneça uma senha temporária e oriente a troca no primeiro acesso.
*   Revise mensalmente a lista de usuários ativos para garantir a segurança dos dados.

---
*Manual gerado em 29/12/2025*
