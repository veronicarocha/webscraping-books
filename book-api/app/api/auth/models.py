import os
import logging

logger = logging.getLogger(__name__)

def get_users_config():
    """configuração de usuários - compatível local e prod"""
    
    users_config = {
        'admin': {
            'password': os.environ.get('ADMIN_PASSWORD', 'admin123'),  
            'role': 'admin'
        },
        'ml_engineer': {
            'password': os.environ.get('ML_ENGINEER_PASSWORD', 'ml123'), 
            'role': 'ml_engineer'
        }
    }
    
    # Log informativo (sem senhas)
    logger.info("Sistema de autenticação carregado")
    for username, config in users_config.items():
        env_used = "variável ambiente" if os.environ.get(f'{username.upper()}_PASSWORD') else "valor padrão"
        logger.info(f"Usuário: {username} | Role: {config['role']} | Fonte: {env_used}")
    
    return users_config

USERS = get_users_config()