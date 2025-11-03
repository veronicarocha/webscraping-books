from dotenv import load_dotenv
load_dotenv()  # Carrega variáveis do .env

import os
from datetime import timedelta
from urllib.parse import urlparse

class Config:
    # fallback para desenvolvimento
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')  
    
    @staticmethod
    def get_database_url():
        """
        Retorna a URL do banco correta para cada ambiente
        """
        # Verifica se está no Railway
        is_railway = os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RAILWAY_SERVICE_NAME')
        
        if is_railway:
            database_url = os.environ.get('DATABASE_URL')
            if database_url and database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            return database_url
        else:
            public_db_url = os.environ.get('DATABASE_URL')
            if public_db_url and public_db_url.startswith('postgres://'):
                public_db_url = public_db_url.replace('postgres://', 'postgresql://', 1)
            return public_db_url or 'sqlite:///books.db'
    
    SQLALCHEMY_DATABASE_URI = get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Config
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    JSON_AS_ASCII = False  
    JSONIFY_PRETTYPRINT_REGULAR = True 
    JSON_SORT_KEYS = False

    @classmethod
    def check_environment(cls):
        """Verifica se está em prod ou des"""
        is_railway = os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RAILWAY_SERVICE_NAME')
        return "produção (Railway)" if is_railway else "desenvolvimento (local)"
    
    @classmethod 
    def get_db_info(cls):
        """Retorna informações da conexão do banco (pra debug)"""
        url = cls.SQLALCHEMY_DATABASE_URI
        if not url:
            return "Nenhuma URL configurada"
        
        if url.startswith('sqlite'):
            return "SQLite (local)"
        else:
            try:
                parsed = urlparse(url)
                host_info = f"{parsed.hostname}:{parsed.port}" if parsed.port else parsed.hostname
                return f"PostgreSQL - {host_info}"
            except Exception as e:
                return f"Database configurado (erro ao parsear: {e})"

# Log de configuração (FORA da classe)
env = Config.check_environment()
print(f" >>> Modo: {env}")
print(f" >>> Database: {Config.get_db_info()}")

# Debug adicional
if "local" in env.lower():
    db_url = Config.SQLALCHEMY_DATABASE_URI
    if db_url and "ballast.proxy.rlwy.net" in db_url:
        print(" >>> Usando URL PÚBLICA do Railway (ballast.proxy.rlwy.net)")
    elif db_url and "railway.internal" in db_url:
        print(" >>> Usando URL INTERNA do Railway (railway.internal)")
    elif db_url and "sqlite" in db_url:
        print(" >>> Usando SQLite local")