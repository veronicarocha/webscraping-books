import time
from flask import g
from .logger import api_logger  # Agora sempre inicializado

def setup_monitoring(app):
    """Configura middleware de monitoramento"""
    
    @app.before_request
    def start_timer():
        g.request_time = time.time()
    
    @app.after_request
    def log_request(response):
        try:
            api_logger.log_request(response)
        except Exception as e:
            print(f"⚠️  Erro no log_request: {e}")
        return response
    
    @app.teardown_request  
    def log_error(error=None):
        if error:
            try:
                api_logger.logger.error(f"Error: {str(error)}")
            except:
                print(f" Erro crítico: {error}")