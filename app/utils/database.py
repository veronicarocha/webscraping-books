import os
import sys
from dotenv import load_dotenv

def _add_project_root_to_path():
    """Adiciona o diretório raiz do projeto ao sys.path"""
    # Sobe 3 níveis: app/utils/ > app/ e >  webscraping-books/
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

def configurar_database_url():
   
    load_dotenv()
    
    # Prioridade 1: URL pública (funciona em qualquer lugar)
    url_publica = os.environ.get('DATABASE_URL_PUBLIC')
    if url_publica:
        return url_publica
    
    # Prioridade 2: URL do ambiente (pode ser interna)
    url_ambiente = os.environ.get('DATABASE_URL')
    if url_ambiente:
        # Se for URL interna do Railway, loga aviso
        if 'railway.internal' in url_ambiente:
            print("AVISO: URL interna do Railway detectada")
        return url_ambiente
    
    # Erro se nenhuma URL encontrada
    raise ValueError("Nenhuma DATABASE_URL configurada")

def setup_database_environment():
    """
    Configura o ambiente do banco para scripts
    """
    _add_project_root_to_path()
    
    os.environ['DATABASE_URL'] = configurar_database_url()
    
    print(f"Database configurado: {get_db_info()}")
    return os.environ['DATABASE_URL']

def get_db_info():
    """Retorna informações da conexão (para logs)"""
    from urllib.parse import urlparse
    
    url = os.environ.get('DATABASE_URL', '')
    if not url:
        return "Nenhuma URL configurada"
    
    if url.startswith('sqlite'):
        return "SQLite (local)"
    else:
        try:
            parsed = urlparse(url)
            host_info = f"{parsed.hostname}:{parsed.port}" if parsed.port else parsed.hostname
            return f"PostgreSQL - {host_info}"
        except Exception:
            return "Database configurado"