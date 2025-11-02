from flask import request
from flask_restful import Resource
from flasgger import swag_from
from app.models.book import db, Book
from sqlalchemy import func, desc
import logging

logger = logging.getLogger(__name__)

class StatsOverview(Resource):
    @swag_from({
        'tags': ['Opcionais'],
        'responses': {
            200: {
                'description': 'Estatísticas gerais'
            }
        }
    })
    def get(self):
        """Estatísticas gerais"""
        try:
            total_books = Book.query.count()
            avg_price = db.session.query(func.avg(Book.price)).scalar() or 0
            max_price = db.session.query(func.max(Book.price)).scalar() or 0
            min_price = db.session.query(func.min(Book.price)).scalar() or 0
            
            # Distribuição dos ratings
            rating_dist = db.session.query(
                Book.rating, 
                func.count(Book.id)
            ).group_by(Book.rating).all()
            
            return {
                'total_books': total_books,
                'price_statistics': {
                    'average': round(float(avg_price), 2),
                    'max': round(float(max_price), 2),
                    'min': round(float(min_price), 2)
                },
                'rating_distribution': [
                    {'rating': rating, 'count': count} 
                    for rating, count in rating_dist
                ]
            }, 200
            
        except Exception as e:
            logger.error(f"Error - overview stats: {e}")
            return {'error': 'Erro interno no servidor'}, 500

class TopRatedBooks(Resource):
    @swag_from({
        'tags': ['Opcionais'],
        'parameters': [
            {
                'name': 'limit',
                'in': 'query',
                'type': 'integer',
                'default': 10
            }
        ],
        'responses': {
            200: {
                'description': 'Lista os livros com melhor avaliação'
            }
        }
    })
    def get(self):
        """Lista os livros com melhor avaliação"""
        try:
            limit = request.args.get('limit', 10, type=int)
            
            top_books = Book.query.order_by(
                desc(Book.rating), 
                desc(Book.price)
            ).limit(limit).all()
            
            return {
                'books': [book.to_dict() for book in top_books],
                'limit': limit
            }, 200
            
        except Exception as e:
            logger.error(f"Error - top rated books: {e}")
            return {'error': 'Erro interno no servidor'}, 500

class PriceRangeBooks(Resource):
    @swag_from({
        'tags': ['Opcionais'],
        'parameters': [
            {
                'name': 'min',
                'in': 'query',
                'type': 'number',
                'required': True
            },
            {
                'name': 'max',
                'in': 'query',
                'type': 'number',
                'required': True
            },
            {
                'name': 'page',
                'in': 'query',
                'type': 'integer',
                'default': 1
            }
        ],
        'responses': {
            200: {
                'description': 'Filtra livros dentro de uma faixa de preço específica'
            }
        }
    })
    def get(self):
        """Filtra livros dentro de uma faixa de preço específica"""
        try:
            min_price = request.args.get('min', type=float)
            max_price = request.args.get('max', type=float)
            page = request.args.get('page', 1, type=int)
            
            if min_price is None or max_price is None:
                return {'error': 'min and max price são obrigatorios'}, 400
            
            books = Book.query.filter(
                Book.price.between(min_price, max_price)
            ).paginate(
                page=page, 
                per_page=20, 
                error_out=False
            )
            
            return {
                'books': [book.to_dict() for book in books.items],
                'pagination': {
                    'page': page,
                    'per_page': 20,
                    'total': books.total,
                    'pages': books.pages
                },
                'price_range': {
                    'min': min_price,
                    'max': max_price
                }
            }, 200
            
        except Exception as e:
            logger.error(f"Error filtering by price range: {e}")
            return {'error': 'Erro interno no servidor'}, 500