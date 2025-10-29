from flask import request
from flask_restful import Resource
from flasgger import swag_from
from app.models.book import Book
from sqlalchemy import desc
import logging

logger = logging.getLogger(__name__)

class Books(Resource):
    @swag_from({
        'tags': ['Core'],
        'parameters': [
            {
                'name': 'page',
                'in': 'query',
                'type': 'integer',
                'default': 1
            },
            {
                'name': 'per_page',
                'in': 'query',
                'type': 'integer',
                'default': 20
            }
        ],
        'responses': {
            200: {
                'description': 'Lista todos os livros disponíveis',
                'examples': {
                    'application/json': {
                        'books': [],
                        'pagination': {
                            'page': 1,
                            'per_page': 20,
                            'total': 1000,
                            'pages': 50
                        }
                    }
                }
            }
        }
    })
    def get(self):
        """Lista todos os livros disponíveis na base de dados"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            
            books = Book.query.paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            
            return {
                'books': [book.to_dict() for book in books.items],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': books.total,
                    'pages': books.pages
                }
            }, 200
            
        except Exception as e:
            logger.error(f"Error fetching books: {e}")
            return {'error': 'Erro interno no servidor'}, 500

class BookDetail(Resource):
    @swag_from({
        'tags': ['Core'],
        'parameters': [
            {
                'name': 'id',
                'in': 'path',
                'type': 'integer',
                'required': True
            }
        ],
        'responses': {
            200: {
                'description': 'Detalhes completos de um livro específico'
            },
            404: {
                'description': 'Livro não encontrado'
            }
        }
    })
    def get(self, id):
        """Retorna detalhes completos de um livro específico pelo ID"""
        try:
            book = Book.query.get_or_404(id)
            return book.to_dict(), 200
        except Exception as e:
            logger.error(f"Error fetching book {id}: {e}")
            return {'error': 'Livro nao encontrado'}, 404

class BookSearch(Resource):
    @swag_from({
        'tags': ['Core'],
        'parameters': [
            {
                'name': 'title',
                'in': 'query',
                'type': 'string'
            },
            {
                'name': 'category',
                'in': 'query',
                'type': 'string'
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
                'description': 'Busca livros por título E/OU categoria'
            }
        }
    })
    def get(self):
        """Busca livros por título E/OU categoria (combinado quando ambos informados)"""
        try:
            title = request.args.get('title', '')
            category = request.args.get('category', '')
            page = request.args.get('page', 1, type=int)
            
            query = Book.query
            
            if title and category:
                query = query.filter(
                    Book.title.ilike(f'%{title}%'),
                    Book.category.ilike(f'%{category}%')
                )
                search_type = "título E categoria"
            elif title:
                # Apenas título
                query = query.filter(Book.title.ilike(f'%{title}%'))
                search_type = "título"
            elif category:
                # Apenas categoria
                query = query.filter(Book.category.ilike(f'%{category}%'))
                search_type = "categoria"
            else:
                query = query
                search_type = "todos os livros"
            
            books = query.paginate(
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
                'search_filters': {
                    'title': title,
                    'category': category
                },
                'search_type': search_type,
                'results_count': len(books.items)
            }, 200
            
        except Exception as e:
            logger.error(f"Error searching books: {e}")
            return {'error': 'Erro interno no servidor'}, 500