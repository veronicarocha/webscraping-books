import streamlit as st
import pandas as pd
import json
import plotly.express as px
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="Book API - Dashboard", layout="wide")

st.title("📊 Book API - Monitoramento & Analytics")

st.sidebar.header("Configurações")
date_range = st.sidebar.selectbox("Período", ["Últimas 24h", "Última semana", "Último mês"])

def load_logs():
    logs = []
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    log_file = os.path.join(project_root, 'logs', 'api_monitor.log')
    
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            log_data = json.loads(line.strip())
                            logs.append(log_data)
                        except json.JSONDecodeError:
                            continue
            return logs
        except Exception as e:
            st.error(f"Erro ao ler arquivo: {e}")
            return []
    return []

logs = load_logs()

if logs:
    processed_data = []
    
    for log in logs:
        if 'message' in log and isinstance(log['message'], dict):
            row_data = {}
            
            row_data['log_timestamp'] = log.get('timestamp') 
            row_data['level'] = log.get('level')
            row_data['module'] = log.get('module')
            
            # Adicionar todos os campos do message, renomeando o timestamp
            message_data = log['message'].copy()
            if 'timestamp' in message_data:
                row_data['request_timestamp'] = message_data.pop('timestamp')
            
            # Adicionar o resto dos campos do message
            row_data.update(message_data)
            
            processed_data.append(row_data)
    
    # Criar DataFrame
    df = pd.DataFrame(processed_data)
    
    # Converter timestamp principal - ver
    if 'request_timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['request_timestamp'], errors='coerce')
    elif 'log_timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['log_timestamp'], errors='coerce')
    
    # Remover linhas com timestamp inválido
    df = df.dropna(subset=['timestamp'])
    
    if not df.empty:
        # Filtro por data
        if date_range == "Últimas 24h":
            cutoff = datetime.now() - timedelta(hours=24)
        elif date_range == "Última semana":
            cutoff = datetime.now() - timedelta(days=7)
        else:
            cutoff = datetime.now() - timedelta(days=30)
        
        df = df[df['timestamp'] >= cutoff]
        
        # MÉTRICAS PRINCIPAIS
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_requests = len(df)
            st.metric("Total Requisições", total_requests)
        
        with col2:
            if 'status_code' in df.columns:
                error_count = len(df[df['status_code'] >= 400])
                error_rate = (error_count / total_requests * 100) if total_requests > 0 else 0
                st.metric("Taxa de Erro", f"{error_rate:.1f}%")
            else:
                st.metric("Taxa de Erro", "N/A")
        
        with col3:
            if 'processing_time_seconds' in df.columns:
                avg_response_time = df['processing_time_seconds'].mean()
                st.metric("Tempo Médio", f"{avg_response_time:.3f}s")
            else:
                st.metric("Tempo Médio", "N/A")
        
        with col4:
            if 'endpoint' in df.columns:
                unique_endpoints = df['endpoint'].nunique()
                st.metric("Endpoints", unique_endpoints)
            else:
                st.metric("Endpoints", "N/A")
        
        # GRÁFICOS
        if not df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Requests por hora
                df['hour'] = df['timestamp'].dt.floor('H')
                hourly_requests = df.groupby('hour').size().reset_index(name='count')
                
                if not hourly_requests.empty:
                    fig_hourly = px.line(hourly_requests, x='hour', y='count', 
                                        title='Requisições por Hora',
                                        labels={'hour': 'Hora', 'count': 'Requisições'})
                    st.plotly_chart(fig_hourly, use_container_width=True)
            
            with col2:
                # Requests por endpoint
                if 'endpoint' in df.columns:
                    endpoint_counts = df['endpoint'].value_counts().head(10)
                    if not endpoint_counts.empty:
                        fig_endpoints = px.bar(x=endpoint_counts.index, y=endpoint_counts.values,
                                              title='Top 10 Endpoints Mais Acessados',
                                              labels={'x': 'Endpoint', 'y': 'Requisições'})
                        st.plotly_chart(fig_endpoints, use_container_width=True)
            
            # TABELA DE LOGS RECENTES
            st.subheader("📋 Logs Recentes")
            display_columns = ['timestamp', 'method', 'endpoint']
            
            # Adicionar colunas disponíveis
            optional_columns = ['status_code', 'processing_time_seconds', 'ip_address']
            for col in optional_columns:
                if col in df.columns:
                    display_columns.append(col)
            
            if all(col in df.columns for col in display_columns):
                recent_logs = df[display_columns].tail(20)
                st.dataframe(recent_logs.sort_values('timestamp', ascending=False))
            
            # MÉTRICAS DETALHADAS
            st.subheader("⚡ Estatísticas Detalhadas")
            
            if 'endpoint' in df.columns and 'processing_time_seconds' in df.columns and 'status_code' in df.columns:
                endpoint_stats = df.groupby('endpoint').agg({
                    'processing_time_seconds': ['count', 'mean', 'max'],
                    'status_code': lambda x: (x >= 400).sum()
                }).round(3)
                
                endpoint_stats.columns = ['Total', 'Tempo Médio (s)', 'Tempo Máx (s)', 'Erros']
                st.dataframe(endpoint_stats)
            
            # DISTRIBUIÇÃO DE STATUS CODES
            if 'status_code' in df.columns:
                st.subheader("📊 Distribuição de Status Codes")
                status_counts = df['status_code'].value_counts()
                if not status_counts.empty:
                    fig_status = px.pie(values=status_counts.values, names=status_counts.index,
                                       title='Status Codes das Requisições')
                    st.plotly_chart(fig_status, use_container_width=True)
        
        else:
            st.warning("📭 Nenhum dado no período selecionado")
    
    else:
        st.error("❌ Nenhum dado válido para mostrar")

else:
    st.warning("📭 Nenhum log encontrado")
    st.info("💡 Execute algumas requisições na API e atualize esta página")

# Status do sistema
st.sidebar.header("Status do Sistema")
st.sidebar.info(f"📊 Logs carregados: {len(logs)}")
if logs:
    st.sidebar.success("🟢 Sistema de monitoramento ativo")