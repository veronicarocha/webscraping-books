from flask_restful import Resource
from flasgger import swag_from
from app.models.book import db, Book
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)

class Categories(Resource):
    @swag_from({
        'tags': ['Core'],
        'responses': {
            200: {
                'description': 'Lista todas as categorias de livros disponíveis'
            }
        }
    })
    def get(self):
        """Lista todas as categorias de livros disponíveis"""
        try:
            categories = db.session.query(
                Book.category, 
                func.count(Book.id).label('book_count')
            ).group_by(Book.category).all()
            
            return {
                'categories': [
                    {
                        'name': category[0],
                        'book_count': category[1]
                    } for category in categories
                ],
                'total_categories': len(categories)
            }, 200
            
        except Exception as e:
            logger.error(f"Error fetching categories: {e}")
            return {'error': 'Erro interno no servidor'}, 500

class CategoryStats(Resource):
    @swag_from({
        'tags': ['Opcionais'],
        'responses': {
            200: {
                'description': 'Estatísticas detalhadas por categoria'
            }
        }
    })
    def get(self):
        """Estatísticas detalhadas por categoria"""
        try:
            stats = db.session.query(
                Book.category,
                func.count(Book.id).label('book_count'),
                func.avg(Book.price).label('avg_price'),
                func.max(Book.price).label('max_price'),
                func.min(Book.price).label('min_price')
            ).group_by(Book.category).all()
            
            return {
                'category_stats': [
                    {
                        'category': stat.category,
                        'book_count': stat.book_count,
                        'avg_price': round(float(stat.avg_price or 0), 2),
                        'max_price': round(float(stat.max_price or 0), 2),
                        'min_price': round(float(stat.min_price or 0), 2)
                    } for stat in stats
                ]
            }, 200
            
        except Exception as e:
            logger.error(f"Error fetching category stats: {e}")
            return {'error': 'Erro interno no servidor'}, 500