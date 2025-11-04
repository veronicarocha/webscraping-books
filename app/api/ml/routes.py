from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from
from flask import request
from app.models.book import Book
import logging

logger = logging.getLogger(__name__)

class MLFeatures(Resource):
    @jwt_required()
    @swag_from({
        'tags': ['ml'],
        'security': [{'Bearer Auth': []}],
        'responses': {
            200: {
                'description': 'Dados formatados para features de ML',
                'examples': {
                    'application/json': {
                        'features': [
                            {
                                'book_id': 1,
                                'title': 'Book Title',
                                'price': 19.99,
                                'rating': 4,
                                'category': 'Fiction'
                            }
                        ],
                        'total_records': 10,
                        'message': 'ML features - v1'
                    }
                }
            }
        }
    })
    def get(self):
        """Retorna dados formatados para features de ML - V1"""
        try:
            books = Book.query.limit(10).all()
            
            features = []
            for book in books:
                feature_set = {
                    'book_id': book.id,
                    'title': book.title,
                    'price': book.price,
                    'rating': book.rating,
                    'category': book.category
                }
                features.append(feature_set)
            
            return {
                'features': features,
                'total_records': len(features),
                'message': 'ML features - v1'
            }, 200
            
        except Exception as e:
            return {'error': str(e)}, 500

class TrainingData(Resource):
    @jwt_required()
    @swag_from({
        'tags': ['ml'],
        'security': [{'Bearer Auth': []}],
        'responses': {
            200: {
                'description': 'Dataset completo para treinamento de modelos',
                'examples': {
                    'application/json': {
                        'training_data': [
                            {
                                'id': 1,
                                'title': 'Book Title',
                                'price': 19.99,
                                'rating': 4,
                                'category': 'Fiction'
                            }
                        ],
                        'total_samples': 5,
                        'message': 'Training data - v1'
                    }
                }
            }
        }
    })
    def get(self):
        """Dataset para treinamento - V1 """
        try:
            books = Book.query.limit(5).all()
            
            training_data = []
            for book in books:
                data_point = {
                    'id': book.id,
                    'title': book.title,
                    'price': book.price,
                    'rating': book.rating,
                    'category': book.category
                }
                training_data.append(data_point)
            
            return {
                'training_data': training_data,
                'total_samples': len(training_data),
                'message': 'Training data - v1'
            }, 200
            
        except Exception as e:
            return {'error': str(e)}, 500

class Predictions(Resource):
    @jwt_required()
    @swag_from({
        'tags': ['ml'],
        'security': [{'Bearer Auth': []}],
        'parameters': [
            {
                'name': 'body',
                'in': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'user_id': {'type': 'string'},
                        'book_features': {
                            'type': 'array',
                            'items': {
                                'type': 'object'
                            }
                        }
                    }
                }
            }
        ],
        'responses': {
            200: {
                'description': 'Predições geradas com sucesso',
                'examples': {
                    'application/json': {
                        'predictions': [
                            {
                                'book_id': 1,
                                'title': 'Book Title',
                                'predicted_rating': 4.5,
                                'recommendation_score': 0.85
                            }
                        ],
                        'model_version': '1.1-enhanced',
                        'message': 'Predições geradas com sucesso',
                        'user_id': 'user_123',
                        'total_books': 1
                    }
                }
            }
        }
    })
    def post(self):
        """Endpoint para predições """
        try:
            current_user = get_jwt_identity()
            logger.info(f"Endpoint /ml/predictions chamado por: {current_user}")
            
            data = request.get_json()
            
            if not data:
                return {'message': 'Dados JSON não fornecidos'}, 400
            
            user_id = data.get('user_id')
            book_features = data.get('book_features', [])
            
            if not user_id:
                return {'message': 'user_id é obrigatório'}, 400
            
            # Gerar predições 
            predictions = []
            for i, book in enumerate(book_features):
                book_id = book.get('book_id', i + 1)
                original_rating = book.get('rating', 3)
                title = book.get('title', f'Book {book_id}')
                category = book.get('category', 'Unknown')
                price = book.get('price', 25.0)
                
                base_rating = original_rating
                price_factor = max(0.3, 1 - (price / 100))
                category_bonus = {
                    'Fantasy': 0.4, 'Fiction': 0.3, 'Technology': 0.2
                }.get(category, 0.1)
                
                predicted_rating = min(5.0, base_rating + 0.5 + category_bonus)
                recommendation_score = min(1.0, (predicted_rating / 5.0) * price_factor)
                
                predictions.append({
                    'book_id': book_id,
                    'title': title,
                    'predicted_rating': round(predicted_rating, 2),
                    'recommendation_score': round(recommendation_score, 3),
                    'original_rating': original_rating,
                    'category': category
                })
            
            # Ordenar por recommendation_score
            predictions.sort(key=lambda x: x['recommendation_score'], reverse=True)
            
            return {
                'predictions': predictions,
                'model_version': '1.1-enhanced',
                'message': f'Predições geradas para {len(book_features)} livros',
                'user_id': user_id,
                'total_books': len(predictions),
                'user_authenticated': current_user
            }, 200
            
        except Exception as e:
            logger.error(f"Erro no endpoint /ml/predictions: {str(e)}")
            return {
                'message': 'Erro interno ao processar predições',
                'error': str(e)
            }, 500