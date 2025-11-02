from dotenv import load_dotenv
load_dotenv()  # Carrega variáveis do .env

import os
from datetime import timedelta

class Config:
    #fallback para desenvolvimento
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')  
    
    # Database
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or 'sqlite:///books.db'  # como fallback SQLite
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Config
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    JSON_AS_ASCII = False  
    JSONIFY_PRETTYPRINT_REGULAR = True 
    JSON_SORT_KEYS = False

    @classmethod
    def check_environment(cls):
        is_production = all([
            os.environ.get('SECRET_KEY'),
            os.environ.get('JWT_SECRET_KEY'), 
            os.environ.get('DATABASE_URL')
        ])
        
        return "produção" if is_production else "desenvolvimento"

if Config.check_environment() == "produção":
    print(" >>> Modo PRODUÇÃO detectado")
else:
    print(" >>> Modo DESENVOLVIMENTO detectado")