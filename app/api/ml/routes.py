from flask_restful import Resource
from flask_jwt_extended import jwt_required
from flasgger import swag_from
from app.models.book import Book

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
            # Apenas para teste - retorna dados básicos
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
            # Apenas para teste - retorna dados básicos
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
                            {'book_id': 1, 'predicted_rating': 4.5},
                            {'book_id': 2, 'predicted_rating': 3.8}
                        ],
                        'model_version': '1.0-simple',
                        'message': 'Predições de exemplo'
                    }
                }
            }
        }
    })
    def post(self):
        """Endpoint para predições - V1"""
        try:
            from flask import request
            data = request.get_json()
            
            # Placeholder simples
            return {
                'predictions': [
                    {'book_id': 1, 'predicted_rating': 4.5},
                    {'book_id': 2, 'predicted_rating': 3.8}
                ],
                'model_version': '1.0-simple',
                'message': 'Predições de exemplo'
            }, 200
            
        except Exception as e:
            return {'error': str(e)}, 500