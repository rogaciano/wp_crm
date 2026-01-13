# Fluxo de Trabalho Git - CRM WP

## Branches do Projeto

| Branch | Descrição |
|--------|-----------|
| `main` | Versão estável (produção) |
| `develop` | Desenvolvimento de novas features |

---

## Comandos Básicos

### Ver branch atual
```bash
git branch
```

### Trocar de branch
```bash
git checkout main      # Ir para produção
git checkout develop   # Ir para desenvolvimento
```

### Criar novo branch a partir do atual
```bash
git checkout -b nome-do-branch
```

---

## Fluxo de Desenvolvimento

### 1. Desenvolver no `develop`
```bash
git checkout develop
# ... fazer mudanças ...
git add -A
git commit -m "feat: descrição da mudança"
git push origin develop
```

### 2. Quando pronto para produção
```bash
# Vai para main
git checkout main

# Traz as mudanças do develop
git merge develop

# Envia para o servidor
git push origin main
```

### 3. Atualizar develop com mudanças da main (se necessário)
```bash
git checkout develop
git merge main
git push origin develop
```

---

## Deploy no Servidor

Após fazer merge na `main`:

```bash
# SSH no servidor
ssh usuario@servidor

# Vai para o diretório do projeto
cd /var/www/wp_crm

# Atualiza o código
git pull origin main

# Migra banco de dados (se necessário)
cd backend && python manage.py migrate

# Rebuild do frontend (se necessário)
cd ../frontend && npm run build

# Reinicia o serviço
sudo systemctl restart wp_crm.service
```

---

## Convenção de Commits

| Prefixo | Uso |
|---------|-----|
| `feat:` | Nova funcionalidade |
| `fix:` | Correção de bug |
| `docs:` | Documentação |
| `style:` | Formatação (não afeta código) |
| `refactor:` | Refatoração |
| `test:` | Testes |

Exemplo: `git commit -m "feat: adicionar filtro por canal na lista de contas"`
