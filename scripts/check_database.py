import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Forçar recarregar config
if 'app' in sys.modules:
    del sys.modules['app']
if 'config' in sys.modules:
    del sys.modules['config']

from config import Config

def check_config():
    print(" Verificando config do Flask...")
    
    config = Config()
    
    print(f" SQLALCHEMY_DATABASE_URI: {config.SQLALCHEMY_DATABASE_URI}")
    
    # Verificar se o arquivo existe
    if 'sqlite:///' in config.SQLALCHEMY_DATABASE_URI:
        db_path = config.SQLALCHEMY_DATABASE_URI.replace('sqlite:///', '')
        if os.path.exists(db_path):
            size = os.path.getsize(db_path)
            print(f" Arquivo encontrado: {db_path} ({size} bytes)")
        else:
            print(f" Arquivo NÃO encontrado: {db_path}")

if __name__ == '__main__':
    check_config()