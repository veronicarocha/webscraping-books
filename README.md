# Book API - API Completa para Gestão e Recomendação de Livros

## 📖 Descrição
API REST completa para consulta, gestão e recomendação de livros com sistema de machine learning integrado. Desenvolvida com arquitetura modular e escalável, incluindo monitoramento em tempo real.

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
```bash
git https://github.com/veronicarocha/webscraping-books
cd webscraping-books/book-api