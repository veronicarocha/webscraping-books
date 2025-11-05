# Book API - API Completa para Gestão e Recomendação de Livros

## 📖 Descrição
API REST completa para consulta, gestão e recomendação de livros com sistema de machine learning integrado. Desenvolvida com arquitetura modular e escalável, incluindo monitoramento em tempo real.
O projeto é composto por um pipeline completo, que vai desde a ingestão e raspagem de dados (scraping) até a exposição dos dados via API pública, com monitoramento e métricas em Streamlit.

## Dados produtivos ##

**URL DA APLICAÇÃO:**

https://web-production-962ea.up.railway.app

Apontando para rota específica:
https://web-production-962ea.up.railway.app/api/v1/health


**URL DO DASHBOARD:**
https://streamlit-dashboard-production-f9ea.up.railway.app


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
```

### Recomendações ###
### VSCode

Editor de código recomendado para o projeto: VSCode.

# Pré requisitos #

## Python
Tenha o python criado e configurado na maquina  (utilizado python-3.11.9)
https://www.python.org/
Na instalação IMPORTANTE marcar "Add Python to PATH"

Verifique no terminal a versao instalada (Reinicie o terminal):

```python --version ```

## Node 
interessante também instalar o Node para utilizar (quando e se necessário) npm install xxxx


## Instalar Dependencias ##

Depois crie a venv e instale as dependencias do projeto (comandos no terminal):

```
python -m venv venv
source venv/bin/activate  # ou source venv\Scripts\activate 
pip install -r requirements.txt
```

### 2. Variaveis de ambiente
crie um arquivo na raiz do projeto .env com o conteudo abaixo: 

```bash
SECRET_KEY=minha-chave-super-secreta-local
JWT_SECRET_KEY=jwt-chave-secreta-local
DATABASE_URL=postgresql://postgres:senha@localhost:5432/bookapi
ML_ENGINEER_PASSWORD=senha_ml_local
```

### Pré requisito
Instalar o Docker e Postgres 

```
https://www.docker.com/products/docker-desktop/
ou
https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe
```

### 3. Setup da base

Quando o docker estiver rodando, volte para o terminal e digite:

```
docker run --name postgres-bookapi -e POSTGRES_PASSWORD=senha -e POSTGRES_DB=bookapi -p 5432:5432 -d postgres:15

```
Para verificar se o postgres está rodando, execute o comando: 
```docker ps ```

Se o container estiver rodando corretamente, executar o setup:
```python scripts/setup_database.py ```

Terá um retorno tipo:

```
 python scripts/setup_database.py
 >>> Modo: desenvolvimento (local)
 >>> Database: PostgreSQL - localhost:5432
✅ Tabelas criadas com sucesso!
✅ Conexão com PostgreSQL testada!
📊 Total de livros no banco: 0
```

### 3. Iniciar Serviços
Rode os comandos abaixo em terminais separados:

# Terminal 1 - API Book-API:

```bash
python run.py
# API: http://localhost:5000
# Docs: http://localhost:5000/apidocs

```
Esse comando também verifica se a base está completa ou se precisa realizar o scraping dos dados ainda.

Terá um retorno como:

´´´

 python run.py
 >>> Modo: desenvolvimento (local)
 >>> Database: PostgreSQL - localhost:5432
>>> Tabelas criadas
>>>  Análise da Base:
>>>  Livros: 1
>>>  Categorias: 1
>>> INICIANDO SCRAPING INTELIGENTE
>>>   Meta: 1000 livros
>>>   Limite: 15 minutos
>>>   Offset: 1 categorias
2025-11-04 23:16:09,068 - app.services.scraper - INFO -  >>> BookScraper inicializado com sucesso
2025-11-04 23:16:09,645 - app.services.scraper - INFO - Encontradas 50 categorias
>>>    📂 Categorias para processar: 49/50
>>> [2/50] Processando: Mystery
>>>    Tempo: 0.0min | Livros: 1/1000
2025-11-04 23:16:09,660 - app.services.scraper - INFO - Scraping categoria: Mystery
2025-11-04 23:16:09,660 - app.services.scraper - INFO - Scraping página: http://books.toscrape.com/catalogue/category/books/mystery_3/index.html
2025-11-04 23:16:13,875 - app.services.scraper - INFO - Scraping página: http://books.toscrape.com/catalogue/category/books/mystery_3/page-2.html
2025-11-04 23:16:17,027 - app.services.scraper - INFO - ✅ Mystery: 32 livros coletados
>>> Mystery: +32 novos,0 existentes
>>> [3/50] Processando: Historical Fiction
>>>    Tempo: 0.2min | Livros: 33/1000
2025-11-04 23:16:18,116 - app.services.scraper - INFO - Scraping categoria: Historical Fiction
2025-11-04 23:16:18,116 - app.services.scraper - INFO ....

´´´

E já terá acessível as rotas como :

http://localhost:5000/apidocs/

http://localhost:5000/api/v1/books?per_page=6


# Terminal 2 - Dashboard:
entrar na pasta do dashboard e instalar as dependencias do dashboard

cd dashboard

```pip install -r requirements.txt```


Só depois subir a aplicação em si.

```bash
cd dashboard
streamlit run app.py
# Dashboard: http://localhost:8501
```

### 4. Popular Banco de Dados

Caso a base nao tenha ficado como esperado (1000 livros), com os dados carregados:
Os scrits abaixo podem ser utilizados para "equalizar" a base

```bash
python scripts/concilia_scraping.py
ou
python scripts/complete_scraping.py 
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


### 8. Plano Arquitetural – Book API

<div>
 <img src="resourses/desenho-aplicacao.png" width="800" height="700" alt="desenho_arquitetura" /> 
</div>




## 🧩 Arquitetura do Sistema

| Componente | Descrição |
|-------------|------------|
| **Scraper (Python)** | Executa a raspagem do site e coleta dados atualizados dos livros. Pode ser disparado manualmente ou automaticamente. |
| **ETL / Transformação** | Processa, limpa e estrutura os dados antes de salvar no banco de dados PostgreSQL. |
| **Banco de Dados (PostgreSQL)** | Armazena as informações dos livros (id, título, preço, rating, categoria, etc). |
| **API Flask** | Fornece endpoints RESTful para consulta, análise e operações sobre os dados. |
| **Painel Streamlit** | Exibe métricas de uso, estatísticas de livros e monitora a saúde das rotas da API. |


### 9. Documentação das rotas da API

Collection para testes no POSTMAN disponivel no projeto

# CATÁLOGO DE ENDPOINTS
## 🔧 CORE ENDPOINTS
| Método	| Rota 					| 	Descrição |
|---------|---------------|------------|
| GET	| /api/v1/health			|Health check da API |
| POST	| /api/v1/scraping/trigger	|Disparar scraping manual|

## 📚 BOOKS ENDPOINTS
| Método	| Rota                    |	Descrição                   |
|---------|------------------------|-----------------------------|
| GET |	/api/v1/books			      	| Listar todos os livros          |
| GET |	/api/v1/books/<int:id>		| Detalhes de um livro específico |
| GET |	/api/v1/books/search		| Buscar livros                   |
| GET |	/api/v1/books/top-rated		| Livros mais bem avaliados       |
| GET |	/api/v1/books/price-range	| Livros por faixa de preço       |

## 🏷️ CATEGORIES ENDPOINTS
| Método| 	Rota					| Descrição						|
|---------|---------------|---------------------|
| GET	| /api/v1/categories		| Listar todas as categorias	|
| GET	| /api/v1/stats/categories	| Estatísticas por categoria	|

## 📊 STATS ENDPOINTS
| Método |	Rota	        | Descrição |
|---------|---------------|------------|
| GET	 | /api/v1/stats/overview	|Visão geral das estatísticas|

## 🔐 AUTH ENDPOINTS
| Método| 	Rota				| Descrição					|
|---------|---------------|------------|
| POST	| /api/v1/auth/login	| Login e obtenção de token |
| POST	| /api/v1/auth/refresh	| Refresh do token JWT      |

## 🤖 ML ENDPOINTS
| Método| 	Rota					| Descrição						|
|---------|---------------|------------|
| GET	| /api/v1/ml/features		| Features para machine learning|
| GET	| /api/v1/ml/training-data	| Dados de treinamento			|
| GET	| /api/v1/ml/predictions	| Previsões do modelo			|

## 🐛 DEBUG ENDPOINTS
| Método| 	Rota				| Descrição			|
|---------|---------------|------------|
| GET	| /api/v1/debug/logs	| Acessar logs da API  |


### 10 . Exemplos de chamadas com requests/responses

Para acesso à documentação acesse: https://web-production-962ea.up.railway.app/apidocs/#/


## 11. Considerações de Manutenção e Escalabilidade
  - O scraping pode ser agendado via cron job ou Airflow (futuro).
  - Implementar um sistema de autenticação JWT
  - A API é desacoplada do processo de ingestão, podendo escalar separadamente.
  - O Streamlit pode ser hospedado independentemente, consumindo a API por HTTPS.
  - Logs e métricas podem ser adicionados (Prometheus + Grafana).