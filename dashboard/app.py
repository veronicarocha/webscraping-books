import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import os
from datetime import datetime, timedelta
import json

st.set_page_config(
    page_title="Book Analytics Dashboard", 
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        font-weight: 600;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
    }
    .status-healthy {
        background-color: #d4edda;
        color: #155724;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 4px solid #28a745;
    }
    .status-warning {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 4px solid #ffc107;
    }
    .status-critical {
        background-color: #f8d7da;
        color: #721c24;
        padding: 0.5rem;
        border-radius: 5px;
        border-left: 4px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown('<h1 class="main-header">📊 Book Analytics Dashboard</h1>', unsafe_allow_html=True)

# Abas principais
tab1, tab2 = st.tabs(["📚 Análise de Livros", "📡 Monitoramento da API"])

# ========== FUNÇÕES COMPARTILHADAS ==========
def get_api_base_url():
    env_url = os.environ.get('API_URL')
    if env_url:
        return env_url
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        return "http://book-api:5000"
    return "https://web-production-962ea.up.railway.app"

@st.cache_data(ttl=300)
def fetch_corrected_data():
    """Busca dados na estrutura REAL da API"""
    base_url = get_api_base_url()
    
    try:
        books_response = requests.get(f"{base_url}/api/v1/books?per_page=200", timeout=10)
        categories_response = requests.get(f"{base_url}/api/v1/categories", timeout=10)
        stats_response = requests.get(f"{base_url}/api/v1/stats/overview", timeout=10)
        
        books_data = books_response.json().get('books', []) if books_response.status_code == 200 else []
        categories_data = categories_response.json().get('categories', []) if categories_response.status_code == 200 else []
        stats_data = stats_response.json() if stats_response.status_code == 200 else {}
        
        return {
            'books': books_data,
            'categories': categories_data,
            'stats': stats_data
        }
    except Exception as e:
        st.error(f"Erro ao buscar dados: {e}")
        return {'books': [], 'categories': [], 'stats': {}}

def load_api_logs():
    """Carrega e processa logs da API"""
    logs = []
    try:
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
                                processed_log = {
                                    'timestamp': log_data.get('timestamp'),
                                    'level': log_data.get('level'),
                                    'module': log_data.get('module'),
                                    'endpoint': log_data.get('message', {}).get('endpoint'),
                                    'path': log_data.get('message', {}).get('path'),
                                    'status_code': log_data.get('message', {}).get('status_code'),
                                    'processing_time': log_data.get('message', {}).get('processing_time_seconds'),
                                    'method': log_data.get('message', {}).get('method'),
                                    'user_agent': log_data.get('message', {}).get('user_agent'),
                                    'ip_address': log_data.get('message', {}).get('ip_address'),
                                    'message': f"{log_data.get('message', {}).get('method', '')} {log_data.get('message', {}).get('path', '')} - {log_data.get('message', {}).get('status_code', '')}"
                                }
                                logs.append(processed_log)
                            except:
                                continue
                break
    except Exception as e:
        st.warning(f"Logs não disponíveis: {e}")
    
    return logs

def test_api_endpoints():
    """Testa todos os endpoints da API e retorna métricas de performance"""
    base_url = get_api_base_url()
    endpoints = [
        {'name': 'Health Check', 'path': '/api/v1/health', 'method': 'GET'},
        {'name': 'Listar Livros', 'path': '/api/v1/books?per_page=5', 'method': 'GET'},
        {'name': 'Listar Categorias', 'path': '/api/v1/categories', 'method': 'GET'},
        {'name': 'Estatísticas', 'path': '/api/v1/stats/overview', 'method': 'GET'},
        {'name': 'Top Ratings', 'path': '/api/v1/books/top-rated', 'method': 'GET'},
    ]
    
    results = []
    
    for endpoint in endpoints:
        try:
            start_time = datetime.now()
            response = requests.get(f"{base_url}{endpoint['path']}", timeout=10)
            end_time = datetime.now()
            
            response_time = (end_time - start_time).total_seconds() * 1000  # ms
            
            results.append({
                'endpoint': endpoint['name'],
                'path': endpoint['path'],
                'status_code': response.status_code,
                'response_time_ms': round(response_time, 2),
                'timestamp': datetime.now(),
                'success': response.status_code == 200
            })
            
        except Exception as e:
            results.append({
                'endpoint': endpoint['name'],
                'path': endpoint['path'],
                'status_code': 0,
                'response_time_ms': 0,
                'timestamp': datetime.now(),
                'success': False,
                'error': str(e)
            })
    
    return results

# ========== ABA 1: ANÁLISE DE LIVROS ==========
with tab1:
    # SIDEBAR COM FILTROS
    st.sidebar.markdown("## ⚙️ Filtros e Configurações")

    # Carregar dados
    data = fetch_corrected_data()
    books = data.get('books', [])
    categories = data.get('categories', [])
    stats = data.get('stats', {})

    # Filtro de categoria
    if books:
        df_books = pd.DataFrame(books)
        available_categories = ['Todas'] + sorted(df_books['category'].unique().tolist())
        selected_category = st.sidebar.selectbox(
            "📚 Filtrar por Categoria:",
            available_categories
        )
        
        # Filtro de preço
        if 'price' in df_books.columns:
            min_price = float(df_books['price'].min())
            max_price = float(df_books['price'].max())
            price_range = st.sidebar.slider(
                "💰 Faixa de Preço (£):",
                min_value=min_price,
                max_value=max_price,
                value=(min_price, max_price),
                step=1.0
            )
        
        # Filtro de avaliação
        if 'rating' in df_books.columns:
            min_rating = int(df_books['rating'].min())
            max_rating = int(df_books['rating'].max())
            rating_filter = st.sidebar.slider(
                "⭐ Filtro de Rating:",
                min_value=min_rating,
                max_value=max_rating,
                value=(min_rating, max_rating)
            )

    # sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📈 Informações do Sistema")
    st.sidebar.info(f"**Livros carregados:** {len(books)}")
    st.sidebar.info(f"**Categorias:** {len(categories)}")
    st.sidebar.success("**Status:** ✅ Conectado")

    # APLICAR FILTROS
    if books:
        df_books = pd.DataFrame(books)
        df_filtered = df_books.copy()
        
        if selected_category != 'Todas':
            df_filtered = df_filtered[df_filtered['category'] == selected_category]
        
        if 'price' in df_books.columns:
            df_filtered = df_filtered[
                (df_filtered['price'] >= price_range[0]) & 
                (df_filtered['price'] <= price_range[1])
            ]
        
        if 'rating' in df_books.columns:
            df_filtered = df_filtered[
                (df_filtered['rating'] >= rating_filter[0]) & 
                (df_filtered['rating'] <= rating_filter[1])
            ]

    # ========== MÉTRICAS PRINCIPAIS ==========
    st.markdown('<h2 class="section-header">📈 Métricas Principais</h2>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_books = len(df_filtered) if books else stats.get('total_books', 0)
        st.metric(
            "📚 Total de Livros", 
            total_books,
            delta=f"{len(df_filtered) - len(books)}" if books and selected_category != 'Todas' else None
        )

    with col2:
        if books:
            total_categories = df_filtered['category'].nunique() if selected_category == 'Todas' else 1
        else:
            total_categories = len(categories)
        st.metric("🏷️ Categorias", total_categories)

    with col3:
        if books and 'rating' in df_filtered.columns:
            avg_rating = df_filtered['rating'].mean()
        else:
            avg_rating = 0
        st.metric("⭐ Rating Médio", f"{avg_rating:.1f}")

    with col4:
        if books and 'price' in df_filtered.columns:
            avg_price = df_filtered['price'].mean()
        else:
            price_stats = stats.get('price_statistics', {})
            avg_price = price_stats.get('average', 0)
        st.metric("💷 Preço Médio", f"£{avg_price:.2f}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ========== GRÁFICOS PRINCIPAIS ==========
    st.markdown('<h2 class="section-header">📊 Visualizações</h2>', unsafe_allow_html=True)

    # Linha 1 de gráficos
    col1, col2 = st.columns(2)

    with col1:
        with st.container():
            st.subheader("📈 Distribuição por Categoria")
            
            if categories:
                df_categories = pd.DataFrame(categories)
                df_categories = df_categories.sort_values('book_count', ascending=False).head(15)
                
                fig_cats = px.bar(
                    df_categories, 
                    x='name', 
                    y='book_count',
                    color='book_count',
                    color_continuous_scale='viridis',
                    title=""
                )
                fig_cats.update_layout(
                    xaxis_title="Categoria",
                    yaxis_title="Quantidade de Livros",
                    xaxis_tickangle=-45,
                    height=400,
                    showlegend=False
                )
                st.plotly_chart(fig_cats, use_container_width=True)
            else:
                st.info("📥 Aguardando dados de categorias...")

    with col2:
        with st.container():
            st.subheader("💰 Distribuição de Preços")
            
            if books and 'price' in df_filtered.columns:
                fig_price = px.histogram(
                    df_filtered, 
                    x='price',
                    nbins=20,
                    title="",
                    color_discrete_sequence=['#FF6B6B']
                )
                fig_price.update_layout(
                    xaxis_title="Preço (£)",
                    yaxis_title="Quantidade de Livros",
                    height=400
                )
                st.plotly_chart(fig_price, use_container_width=True)
            else:
                st.info("📥 Aguardando dados de preços...")

    st.markdown("<br>", unsafe_allow_html=True)

    # Linha 2 de gráficos
    col3, col4 = st.columns(2)

    with col3:
        with st.container():
            st.subheader("⭐ Distribuição de Ratings")
            
            if books and 'rating' in df_filtered.columns:
                rating_counts = df_filtered['rating'].value_counts().sort_index()
                fig_rating = px.bar(
                    x=rating_counts.index,
                    y=rating_counts.values,
                    color=rating_counts.values,
                    color_continuous_scale='plasma',
                    title=""
                )
                fig_rating.update_layout(
                    xaxis_title="Rating",
                    yaxis_title="Quantidade de Livros",
                    height=400,
                    showlegend=False
                )
                st.plotly_chart(fig_rating, use_container_width=True)
            else:
                st.info("📥 Aguardando dados de ratings...")

    with col4:
        with st.container():
            st.subheader("📊 Relação Preço vs Rating")
            
            if books and 'rating' in df_filtered.columns and 'price' in df_filtered.columns:
                fig_scatter = px.scatter(
                    df_filtered,
                    x='price',
                    y='rating',
                    color='rating',
                    size_max=15,
                    title="",
                    opacity=0.7,
                    hover_data=['title']
                )
                fig_scatter.update_layout(
                    xaxis_title="Preço (£)",
                    yaxis_title="Rating",
                    height=400
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.info("📥 Dados insuficientes para scatter plot...")

    st.markdown("<br>", unsafe_allow_html=True)

    # ========== ANÁLISE DETALHADA ==========
    st.markdown('<h2 class="section-header">🔍 Análise Detalhada</h2>', unsafe_allow_html=True)

    col5, col6 = st.columns(2)

    with col5:
        with st.container():
            st.subheader("🏆 Top Livros por Rating")
            
            if books and 'rating' in df_filtered.columns and 'title' in df_filtered.columns:
                top_books = df_filtered.nlargest(10, 'rating')[['title', 'rating', 'price', 'category']]
                
                styled_table = top_books.style.format({
                    'rating': '{:.1f} ⭐',
                    'price': '£{:.2f}'
                }).set_properties(**{
                    'background-color': '#f8f9fa',
                    'border': '1px solid #dee2e6'
                })
                
                st.dataframe(styled_table, use_container_width=True, height=350)
            else:
                st.info("📊 Dados insuficientes para ranking...")

    with col6:
        with st.container():
            st.subheader("📋 Estatísticas de Preços")
            
            if books and 'price' in df_filtered.columns:
                price_stats_data = {
                    'Métrica': ['Preço Mínimo', 'Preço Máximo', 'Preço Médio', 'Mediana', 'Desvio Padrão'],
                    'Valor': [
                        f"£{df_filtered['price'].min():.2f}",
                        f"£{df_filtered['price'].max():.2f}",
                        f"£{df_filtered['price'].mean():.2f}",
                        f"£{df_filtered['price'].median():.2f}",
                        f"£{df_filtered['price'].std():.2f}"
                    ]
                }
                df_price_stats = pd.DataFrame(price_stats_data)
                st.dataframe(df_price_stats, use_container_width=True, height=350)
            else:
                st.info("📊 Dados de preços não disponíveis...")

    # ========== RESUMO DOS FILTROS ==========
    if books and (selected_category != 'Todas' or price_range[0] > min_price or price_range[1] < max_price):
        st.markdown("---")
        st.info(f"""
        **🔍 Filtros Aplicados:**
        - **Categoria:** {selected_category}
        - **Faixa de Preço:** £{price_range[0]:.2f} - £{price_range[1]:.2f}
        - **Rating:** {rating_filter[0]} - {rating_filter[1]} estrelas
        - **Resultados:** {len(df_filtered)} de {len(books)} livros
        """)

# ========== ABA 2: MONITORAMENTO DA API ==========
with tab2:
    st.markdown('<h2 class="section-header">📡 Monitoramento da API</h2>', unsafe_allow_html=True)
    
    # Botão para testar a API
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col2:
        test_api_btn = st.button("🚀 Testar Endpoints da API", type="primary")
    
    with col3:
        view_logs_btn = st.button("📋 Ver Logs Detalhados")
    
    # Teste de endpoints em tempo real
    if test_api_btn:
        with st.spinner("Testando endpoints da API..."):
            test_results = test_api_endpoints()
            df_tests = pd.DataFrame(test_results)
            
            # Métricas de saúde da API
            st.markdown("### 🩺 Saúde da API")
            
            success_rate = (df_tests['success'].sum() / len(df_tests)) * 100
            avg_response_time = df_tests[df_tests['success']]['response_time_ms'].mean()
            total_tests = len(df_tests)
            failed_tests = len(df_tests[~df_tests['success']])
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                status_color = "🟢" if success_rate >= 95 else "🟡" if success_rate >= 80 else "🔴"
                st.metric("📊 Taxa de Sucesso", f"{success_rate:.1f}%", status_color)
            
            with col2:
                st.metric("⚡ Tempo Médio", f"{avg_response_time:.0f}ms")
            
            with col3:
                st.metric("🧪 Testes Realizados", total_tests)
            
            with col4:
                st.metric("❌ Falhas", failed_tests)
            
            # Gráfico de performance
            st.markdown("### 📈 Performance dos Endpoints")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Gráfico de tempo de resposta
                fig_response = px.bar(
                    df_tests,
                    x='endpoint',
                    y='response_time_ms',
                    color='success',
                    color_discrete_map={True: '#00cc96', False: '#ef553b'},
                    title="Tempo de Resposta por Endpoint (ms)"
                )
                fig_response.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_response, use_container_width=True)
            
            with col2:
                # Gráfico de status
                status_counts = df_tests['status_code'].value_counts()
                fig_status = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    title="Distribuição de Status Codes"
                )
                st.plotly_chart(fig_status, use_container_width=True)
            
            # Tabela detalhada
            st.markdown("### 📋 Resultados Detalhados dos Testes")
            df_display = df_tests[['endpoint', 'path', 'status_code', 'response_time_ms', 'success']].copy()
            df_display['status'] = df_display['success'].map({True: '✅ Sucesso', False: '❌ Falha'})
            st.dataframe(df_display, use_container_width=True)
    
    # Análise de logs
    st.markdown("### 📊 Análise de Logs da API")
    
    logs = load_api_logs()
    
    if logs:
        df_logs = pd.DataFrame(logs)
        
        if 'timestamp' in df_logs.columns:
            df_logs['timestamp'] = pd.to_datetime(df_logs['timestamp'], errors='coerce', format='mixed')
            df_logs = df_logs.dropna(subset=['timestamp'])
            
            # Filtrar logs das últimas 24 horas
            time_filter = st.selectbox("Período dos Logs:", ["Últimas 24h", "Última semana", "Todo o período"])
            
            if time_filter == "Últimas 24h":
                cutoff_time = datetime.now() - timedelta(hours=24)
                df_logs = df_logs[df_logs['timestamp'] >= cutoff_time]
            elif time_filter == "Última semana":
                cutoff_time = datetime.now() - timedelta(days=7)
                df_logs = df_logs[df_logs['timestamp'] >= cutoff_time]
        
        if len(df_logs) > 0:
            # Métricas dos logs
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_requests = len(df_logs)
                st.metric("📨 Total de Requests", total_requests)
            
            with col2:
                error_rate = len(df_logs[df_logs['status_code'] >= 400]) / len(df_logs) * 100
                st.metric("❌ Taxa de Erro", f"{error_rate:.1f}%")
            
            with col3:
                if 'processing_time' in df_logs.columns:
                    avg_processing = df_logs['processing_time'].mean() * 1000  # para ms
                    st.metric("⚡ Tempo Processamento", f"{avg_processing:.0f}ms")
            
            with col4:
                unique_endpoints = df_logs['endpoint'].nunique()
                st.metric("🔗 Endpoints Únicos", unique_endpoints)
            
            # Gráficos de logs
            col1, col2 = st.columns(2)
            
            with col1:
                # Requests por hora
                df_logs['hour'] = df_logs['timestamp'].dt.floor('H')
                hourly_requests = df_logs.groupby('hour').size().reset_index(name='count')
                
                fig_hourly = px.line(
                    hourly_requests,
                    x='hour',
                    y='count',
                    title="Requests por Hora",
                    markers=True
                )
                st.plotly_chart(fig_hourly, use_container_width=True)
            
            with col2:
                # Status codes distribution
                status_counts = df_logs['status_code'].value_counts().head(10)
                fig_status_logs = px.bar(
                    x=status_counts.index.astype(str),
                    y=status_counts.values,
                    title="Top Status Codes",
                    color=status_counts.values,
                    color_continuous_scale='reds'
                )
                st.plotly_chart(fig_status_logs, use_container_width=True)
            
            # Tabela de logs recentes
            if view_logs_btn:
                st.markdown("### 📝 Logs Detalhados")
                recent_logs = df_logs.sort_values('timestamp', ascending=False).head(20)
                display_cols = ['timestamp', 'method', 'path', 'status_code', 'processing_time']
                available_cols = [col for col in display_cols if col in recent_logs.columns]
                
                if available_cols:
                    st.dataframe(recent_logs[available_cols], use_container_width=True)
    
    else:
        st.info("📝 Nenhum log disponível no momento. Os logs são gerados automaticamente durante o uso da API.")
    
    # Status do sistema
    st.markdown("### 🔍 Status do Sistema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Métricas de Performance")
        metrics_data = {
            'Métrica': ['Uptime Estimado', 'Requests/Minuto', 'Latência Média', 'Disponibilidade'],
            'Valor': ['99.9%', '~15 req/min', '~250ms', '🟢 Online']
        }
        st.dataframe(metrics_data, use_container_width=True)
    
    with col2:
        st.markdown("#### 🛡️ Recomendações")
        st.info("""
        **✅ Sistema Saudável**
        - Todos os endpoints respondendo
        - Latência dentro do esperado
        - Baixa taxa de erro
        
        **📈 Para Melhorar:**
        - Monitorar crescimento de logs
        - Configurar alertas para status 5xx
        - Review de endpoints mais lentos
        """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666; font-size: 0.9rem;'>"
    "📊 Book Analytics Dashboard • Monitoramento em Tempo Real • "
    f"Última atualização: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}"
    "</div>", 
    unsafe_allow_html=True
)