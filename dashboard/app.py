import streamlit as st
import pandas as pd
import json
import plotly.express as px
from datetime import datetime, timedelta
import os
import requests

st.set_page_config(page_title="Book API - Dashboard", layout="wide")
st.title("📊 Book API - Monitoramento")

st.sidebar.header("Configurações")
date_range = st.sidebar.selectbox("Período", ["Últimas 24h", "Última semana", "Último mês"])

def fetch_api_data():
    """Busca os dados da API"""
    try:
        # URL da sua API no Railway
        base_url = "https://web-production-962ea.up.railway.app/api/v1"  # fix url nova
        
        stats_response = requests.get(f"{base_url}/stats/overview")
        books_response = requests.get(f"{base_url}/books?per_page=5")
        categories_response = requests.get(f"{base_url}/categories")
        
        stats = stats_response.json() if stats_response.status_code == 200 else {}
        books = books_response.json() if books_response.status_code == 200 else {}
        categories = categories_response.json() if categories_response.status_code == 200 else {}
        
        return {
            'stats': stats,
            'books': books,
            'categories': categories
        }
    except Exception as e:
        st.error(f"Erro ao conectar com a API: {e}")
        return {}

def load_logs():
    """Tenta carregar logs locais (para dev)"""
    logs = []
    try:
        # Tenta encontrar o arquivo de log
        possible_paths = [
            os.path.join('logs', 'api_monitor.log'),
            os.path.join('..', 'logs', 'api_monitor.log'),
            os.path.join(os.path.dirname(__file__), 'logs', 'api_monitor.log'),
        ]
        
        for log_path in possible_paths:
            if os.path.exists(log_path):
                with open(log_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            try:
                                log_data = json.loads(line.strip())
                                logs.append(log_data)
                            except:
                                continue
                break
    except Exception as e:
        st.warning(f"Logs não disponíveis: {e}")
    
    return logs

api_data = fetch_api_data()

logs = load_logs()

if not api_data.get('stats') and not logs:
    st.warning("📡 Conectando à API...")
    
    # Mostrar informações básicas mesmo sem dados
    st.info("""
    **Para visualizar dados completos:**
    1. Certifique-se que a API está rodando no Railway
    2. Acesse os endpoints:
       - `/api/v1/stats/overview` - Estatísticas gerais
       - `/api/v1/books` - Lista de livros
       - `/api/v1/categories` - Categorias
    """)
    
    # Tentar mostrar dados básicos mesmo sem API
    st.subheader("📊 Informações Básicas")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Status API", "🟢 Online" if api_data else "🟡 Conectando")
    
    with col2:
        st.metric("Modo", "Produção")
    
    with col3:
        st.metric("Dashboard", "Operacional")
    
    st.stop()

if api_data.get('stats'):
    st.subheader("🎯 Estatísticas da API")
    
    stats = api_data['stats']
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_books = stats.get('total_books', 0)
        st.metric("Total Livros", total_books)
    
    with col2:
        total_categories = stats.get('total_categories', 0)
        st.metric("Categorias", total_categories)
    
    with col3:
        avg_rating = stats.get('average_rating', 0)
        st.metric("Rating Médio", f"{avg_rating:.1f}⭐")
    
    with col4:
        avg_price = stats.get('average_price', 0)
        st.metric("Preço Médio", f"£{avg_price:.2f}")

# GRÁFICOS 
if api_data.get('categories'):
    st.subheader("📈 Visualizações")
    
    col1, col2 = st.columns(2)
    
    with col1:
        categories_data = api_data['categories']
        if isinstance(categories_data, list) and len(categories_data) > 0:
            cat_df = pd.DataFrame(categories_data)
            fig_cats = px.bar(cat_df, x='name', y='book_count', 
                            title='Livros por Categoria')
            st.plotly_chart(fig_cats, use_container_width=True)
    
    with col2:
        if api_data.get('books') and isinstance(api_data['books'], list):
            books_df = pd.DataFrame(api_data['books'])
            if 'price' in books_df.columns:
                fig_price = px.histogram(books_df, x='price', 
                                       title='Distribuição de Preços')
                st.plotly_chart(fig_price, use_container_width=True)

if api_data.get('books'):
    st.subheader("📚 Livros Recentes")
    books_data = api_data['books']
    if isinstance(books_data, list) and len(books_data) > 0:
        books_df = pd.DataFrame(books_data)
        display_cols = ['title', 'price', 'rating', 'category']
        available_cols = [col for col in display_cols if col in books_df.columns]
        
        if available_cols:
            st.dataframe(books_df[available_cols].head(10))

# SEÇÃO DE LOGS 
if logs:
    st.subheader("📋 Logs do Sistema")
    
    # Processar logs
    processed_data = []
    for log in logs:
        try:
            if isinstance(log, dict):
                row_data = {
                    'timestamp': log.get('timestamp'),
                    'level': log.get('level'),
                    'message': str(log.get('message', ''))[:100] + '...' if log.get('message') else ''
                }
                processed_data.append(row_data)
        except:
            continue
    
    if processed_data:
        logs_df = pd.DataFrame(processed_data)
        if 'timestamp' in logs_df.columns:
            logs_df['timestamp'] = pd.to_datetime(logs_df['timestamp'], errors='coerce')
            logs_df = logs_df.dropna(subset=['timestamp'])
            st.dataframe(logs_df.tail(10).sort_values('timestamp', ascending=False))

st.sidebar.header("Status do Sistema")
st.sidebar.info(f"📊 Dados da API: {'✅' if api_data else '❌'}")
st.sidebar.info(f"📋 Logs disponíveis: {len(logs)}")
st.sidebar.info(f"📅 Período: {date_range}")
st.sidebar.success("🟢 Dashboard operacional")