# Guia de Publicação na VPS (Ubuntu/Debian)

Este guia assume que o projeto será clonado em `/var/www/wp_crm`.

## 1. Preparação do Servidor

```bash
# Instalar dependências básicas
sudo apt update
sudo apt install python3-pip python3-venv nginx -y

# Instalar o banco de dados que preferir (opcional se já tiver na VPS)
sudo apt install mysql-server -y # ou postgresql postgresql-contrib
```

## 2. Clonar e Configurar Pastas

```bash
cd /var/www
sudo git clone https://github.com/rogaciano/wp_crm.git
sudo chown -R $USER:$USER wp_crm
cd wp_crm
```

## 3. Backend (Django)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt gunicorn

# Criar arquivo .env com suas credenciais de prod
cp .env.example .env
nano .env # Ajuste DEBUG=False, DB_ENGINE e as credenciais do Banco

# Preparar banco e estáticos
python manage.py migrate
python manage.py collectstatic --noinput
```

## 4. Frontend (Vue.js)

**Importante:** Antes de buildar, verifique o arquivo `frontend/.env` para garantir que `VITE_API_URL` aponta para `https://crm.sistema9.com.br/api`.

```bash
cd ../frontend
npm install
npm run build
```

## 5. Configurar Serviços

```bash
# Nginx
sudo cp ../deploy/nginx.conf /etc/nginx/sites-available/crm.sistema9.com.br
sudo ln -s /etc/nginx/sites-available/crm.sistema9.com.br /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Gunicorn (Systemd)
sudo cp ../deploy/gunicorn.service /etc/systemd/system/wp_crm.service
sudo systemctl daemon-reload
sudo systemctl enable wp_crm
sudo systemctl start wp_crm
```

---
**Nota sobre Portas:** 
Se a porta **8001** já estiver sendo usada por outro projeto (verifique com `netstat -tunlp | grep 8001`), altere o número da porta tanto no arquivo `nginx.conf` quanto no `gunicorn.service` para **8002** ou superior.
