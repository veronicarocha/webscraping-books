# Book API - API Completa para Gestão e Recomendação de Livros

## 📖 Descrição
API REST completa para consulta, gestão e recomendação de livros com sistema de machine learning integrado. Desenvolvida com arquitetura modular e escalável, incluindo monitoramento em tempo real.

## Dados produtivos~
URL da aplicação criada no Railway:

https://web-production-962ea.up.railway.app

Ou apontando para rota específica:
https://web-production-962ea.up.railway.app/api/v1/health


## 🏗️ Arquitetura
- **Backend**: Flask + Flask-RESTful
- **Database**: PostgreSQL (Produção) / SQLite (Desenvolvimento)
- **Autenticação**: JWT com roles (admin e ml_engineer)
- **ML**: Sistema de recomendações
- **Monitoramento**: Dashboard Streamlit com analytics
- **Documentação**: Swagger/OpenAPI 
- **Deploy**: Railway
- **Logs**: Estruturados em JSON

## 🚀 Funcionalidades

### 📚 Gestão de Livros
- Listagem paginada de livros
- Busca por título e categoria
- Detalhes completos por ID
- Filtros por faixa de preço
- Livros mais bem avaliados

### 🔐 Autenticação & Segurança
- Login JWT com refresh tokens
- Rotas protegidas por role
- Sistema de usuários (admin, ml_engineer)

### 🤖 Machine Learning
- Features para modelos ML
- Dataset de treinamento
- Sistema de predições
- API para integração com modelos

### 📊 Analytics & Monitoramento
- Estatísticas gerais da coleção
- Métricas por categoria
- Dashboard em tempo real
- Logs estruturados de performance

### 🔧 Utilidades
- Health check da API
- Trigger de scraping
- Documentação interativa Swagger

## 🛠️ Instalação e Desenvolvimento

### 1. Clone o repositório
Realize o clone do projeto:
```bash
git clone https://github.com/veronicarocha/webscraping-books
cd webscraping-books
python -m venv venv
source venv/bin/activate  # ou source venv\Scripts\activate 
pip install -r requirements.txt
```

### 2. Variaveis de ambiente
```bash
DATABASE_URL=postgresql://usuario:senha@localhost/bookapi
JWT_SECRET_KEY=sua-chave-secreta-aqui
ADMIN_USERNAME=admin
ADMIN_PASSWORD=senha-admin
ML_ENGINEER_USERNAME=ml_engineer
ML_ENGINEER_PASSWORD=senha-ml
```

### 3. Iniciar Serviços
Rode os comandos abaixo em terminais separados:

Terminal 1 - API Flask:

```bash
python app.py
# API: http://localhost:5000
# Docs: http://localhost:5000/apidocs

```
Terminal 2 - Dashboard:
```bash
cd dashboard
streamlit run app.py
# Dashboard: http://localhost:8501
```
### 4. Popular Banco de Dados
```bash
python scripts/run_scraper.py
```

### 5. 📡 Uso da API
Pode fazer requests via terminal ou via Swagger para teste
```bash
curl http://localhost:5000/api/v1/health
```


### 6. Autenticação
Algumas rotas são protegidas por usuário e senha 
por enquanto não existe um sistema de cadastro de usuários
basta usar o usuário e senha registrados na aplicação para gerar o token
e utilizar o token nas chamadas necessárias

```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "senha-admin"}'
```


### 7. Dashboard de Monitoramento
Acesse http://localhost:8501 para visualizar:

    - Métricas em tempo real
    - Gráficos de performance
    - Logs da API
    - Estatísticas por endpoint


### 8 . Plano Arquitetural 

### 9. Documentação das rotas da API

### 10 . Exemplos de chamadas com requests/responses
 Instruções para execução. 
