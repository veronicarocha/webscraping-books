import streamlit as st
import pandas as pd
import json
import plotly.express as px
from datetime import datetime, timedelta
import os

st.set_page_config(page_title="Book API - Dashboard", layout="wide")
st.title("📊 Book API - Monitoramento")

st.sidebar.header("Configurações")
date_range = st.sidebar.selectbox("Período", ["Últimas 24h", "Última semana", "Último mês"])

def load_logs():
    logs = []
    log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'api_monitor.log')
    
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            log_data = json.loads(line.strip())
                            # correção - Se message for string, converte para dict
                            if isinstance(log_data.get('message'), str):
                                try:
                                    log_data['message'] = json.loads(log_data['message'])
                                except:
                                    pass
                            logs.append(log_data)
                        except:
                            continue
            return logs
        except Exception as e:
            st.error(f"Erro ao ler logs: {e}")
    return []

logs = load_logs()

if not logs:
    st.warning(" Nenhum log encontrado")
    st.info(" Execute requisições na API e atualize esta página")
    st.stop()

# Processar dados
processed_data = []
for log in logs:
    try:
        message_data = log.get('message', {}) if isinstance(log.get('message'), dict) else log.copy()
        
        row_data = {
            'timestamp': message_data.get('timestamp', log.get('timestamp')),
            'method': message_data.get('method'),
            'endpoint': message_data.get('endpoint'),
            'status_code': message_data.get('status_code'),
            'processing_time': message_data.get('processing_time_seconds')
        }
        processed_data.append(row_data)
    except:
        continue

# Criar DataFrame
df = pd.DataFrame(processed_data)
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
df = df.dropna(subset=['timestamp'])

if df.empty:
    st.error(" Nenhum dado válido para mostrar")
    st.stop()

# ✅ CORREÇÃO: Converter timestamps para o mesmo tipo
df['timestamp'] = df['timestamp'].dt.tz_convert(None)  

# criar filtros por data
now = datetime.now()
if date_range == "Últimas 24h":
    cutoff = now - timedelta(hours=24)
elif date_range == "Última semana":
    cutoff = now - timedelta(days=7)
else:
    cutoff = now - timedelta(days=30)

df = df[df['timestamp'] >= cutoff]

if df.empty:
    st.warning(" Nenhum dado no período selecionado")
    st.stop()

# Métricas principais
st.subheader("Métricas Principais")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Requisições", len(df))

with col2:
    error_count = len(df[df['status_code'] >= 400]) if 'status_code' in df.columns else 0
    error_rate = (error_count / len(df) * 100) if len(df) > 0 else 0
    st.metric("Taxa de Erro", f"{error_rate:.1f}%")

with col3:
    avg_time = df['processing_time'].mean() if 'processing_time' in df.columns else 0
    st.metric("Tempo Médio", f"{avg_time:.3f}s")

with col4:
    unique_eps = df['endpoint'].nunique() if 'endpoint' in df.columns else 0
    st.metric("Endpoints", unique_eps)

# Gráficos
st.subheader("📊 Visualizações")
col1, col2 = st.columns(2)

with col1:
    if 'timestamp' in df.columns:
        df_hourly = df.groupby(df['timestamp'].dt.hour).size()
        fig_hourly = px.line(x=df_hourly.index, y=df_hourly.values, 
                           title='Requisições por Hora', labels={'x': 'Hora', 'y': 'Requisições'})
        st.plotly_chart(fig_hourly, use_container_width=True)

with col2:
    if 'endpoint' in df.columns:
        endpoint_counts = df['endpoint'].value_counts().head(8)
        fig_endpoints = px.bar(x=endpoint_counts.index, y=endpoint_counts.values,
                             title='Endpoints Mais Acessados')
        st.plotly_chart(fig_endpoints, use_container_width=True)

# Tabela de logs
st.subheader("📋 Logs Recentes")
display_cols = ['timestamp', 'method', 'endpoint']
if 'status_code' in df.columns:
    display_cols.append('status_code')
if 'processing_time' in df.columns:
    display_cols.append('processing_time')

st.dataframe(df[display_cols].tail(15).sort_values('timestamp', ascending=False))

# Status do sistema
st.sidebar.header("Status do Sistema")
st.sidebar.info(f"📊 Logs carregados: {len(logs)}")
st.sidebar.info(f"📅 Período: {date_range}")
st.sidebar.success("🟢 Sistema operacional")