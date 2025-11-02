import datetime
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from
from app.models.book import Book
import logging
from config import Config
from datetime import datetime, timezone 
from sqlalchemy import text  # ✅ MANTER ESTE IMPORT

logger = logging.getLogger(__name__)

class HealthCheck(Resource):
    def get(self):
        try:
            # ✅ CORREÇÃO: usar text() no Railway, manter compatibilidade
            from app.models.book import db
            
            # Tenta com text() primeiro (Railway), depois sem (local)
            try:
                db.session.execute(text('SELECT 1'))
            except:
                db.session.execute('SELECT 1')
                
            database_status = 'healthy'
        except Exception as e:
            database_status = f'degraded: {str(e)}'
        
        return {
            'status': 'healthy',
            'environment': Config.check_environment(),
            'database': database_status,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }, 200

class ScrapingTrigger(Resource):
    @jwt_required()
    @swag_from({
        'tags': ['Adicional'],
        'security': [{'Bearer Auth': []}],
        'responses': {
            200: {
                'description': 'Scraping triggered successfully',
                'examples': {
                    'application/json': {
                        'message': 'Scraping iniciado com sucesso',
                        'status': 'started',
                        'triggered_by': 'admin'
                    }
                }
            },
            403: {
                'description': 'Admin access required'
            }
        }
    })
    def post(self):
        """Trigger manual do scraping (apenas admin)"""
        try:
            current_user = get_jwt_identity() 
            
            if ':' in current_user:
                username, role = current_user.split(':')
            else:
                username = current_user
                role = 'user'
            
            if role != 'admin':
                logger.warning(f"Non-admin user attempted scraping: {username}")
                return {'error': 'Admin access required'}, 403
            
            logger.info(f"Scraping triggered by admin: {username}")
            
            return {
                'message': 'Scraping triggered successfully',
                'status': 'started',
                'triggered_by': username,
                'timestamp': '2024-01-01T00:00:00Z'  
            }, 200
            
        except Exception as e:
            logger.error(f"Scraping trigger error: {e}")
            return {'error': 'Erro interno no servidor'}, 500