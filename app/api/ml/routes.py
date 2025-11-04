from urllib import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flasgger import swag_from
from flask import request
from app.models.book import Book
import logging


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


logger = logging.getLogger(__name__)

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
                    'required': ['user_id', 'book_features'],
                    'properties': {
                        'user_id': {
                            'type': 'string',
                            'example': 'user_123'
                        },
                        'book_features': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'book_id': {'type': 'integer', 'example': 1},
                                    'title': {'type': 'string', 'example': 'Book Title'},
                                    'price': {'type': 'number', 'example': 29.99},
                                    'rating': {'type': 'integer', 'example': 4},
                                    'category': {'type': 'string', 'example': 'Fiction'}
                                }
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
                                'recommendation_score': 0.85,
                                'confidence': 0.8,
                                'original_rating': 4,
                                'category': 'Fiction'
                            }
                        ],
                        'model_version': '1.1-enhanced',
                        'message': 'Predições geradas para 3 livros',
                        'user_id': 'user_123',
                        'total_books': 3,
                        'user_authenticated': 'admin:admin',
                        'top_recommendation': {
                            'book_id': 1,
                            'title': 'Book Title', 
                            'predicted_rating': 4.5,
                            'recommendation_score': 0.85,
                            'confidence': 0.8,
                            'original_rating': 4,
                            'category': 'Fiction'
                        }
                    }
                }
            },
            401: {
                'description': 'Não autorizado - token inválido ou ausente'
            },
            400: {
                'description': 'Dados de entrada inválidos'
            },
            500: {
                'description': 'Erro interno do servidor'
            }
        }
    })
    def post(self):
        """
        Gerar predições de recomendação para usuário
        ---
        Versão melhorada com resposta mais rica e validações robustas.
        """
        try:
            # Log para debug
            current_user = get_jwt_identity()
            logger.info(f"Endpoint /ml/predictions chamado por: {current_user}")
            
            # Obter dados da requisição
            data = request.get_json()
            
            if not data:
                logger.error("Nenhum dado JSON recebido")
                return {'message': 'Dados JSON não fornecidos'}, 400
            
            # Validar campos obrigatórios
            user_id = data.get('user_id')
            book_features = data.get('book_features')
            
            if not user_id:
                logger.error("user_id não fornecido")
                return {'message': 'user_id é obrigatório'}, 400
            
            if not book_features or not isinstance(book_features, list):
                logger.error("book_features inválido ou não fornecido")
                return {'message': 'book_features deve ser uma lista não vazia'}, 400
            
            # Log dos dados recebidos
            logger.info(f"Processando predições para user_id: {user_id}, livros: {len(book_features)}")
            
            # Gerar predições melhoradas baseadas nos dados recebidos
            predictions = []
            for i, book in enumerate(book_features):
                book_id = book.get('book_id', i + 1)
                original_rating = book.get('rating', 3)
                price = book.get('price', 25.0)
                category = book.get('category', 'Unknown')
                title = book.get('title', f'Book {book_id}')
                
                base_rating = original_rating
                
                # Fator de preço: livros mais baratos têm melhor score
                price_factor = max(0.3, 1 - (price / 100))
                
                # Bônus por categoria (exemplo)
                category_bonus = {
                    'Fantasy': 0.4,
                    'Fiction': 0.3,
                    'Technology': 0.2,
                    'Travel': 0.1
                }.get(category, 0.1)
                
                # Bônus por rating original
                rating_bonus = (original_rating - 3) * 0.2
                
                # Cálculo da predição
                predicted_rating = min(5.0, base_rating + 0.5 + category_bonus + rating_bonus)
                recommendation_score = min(1.0, (predicted_rating / 5.0) * price_factor)
                confidence = min(0.95, 0.7 + (original_rating * 0.05))
                
                predictions.append({
                    'book_id': book_id,
                    'title': title,
                    'predicted_rating': round(predicted_rating, 2),
                    'recommendation_score': round(recommendation_score, 3),
                    'confidence': round(confidence, 2),
                    'original_rating': original_rating,
                    'category': category,
                    'price': price
                })
            
            # Ordenar por recommendation_score 
            predictions.sort(key=lambda x: x['recommendation_score'], reverse=True)
            
            # Resposta completa
            response_data = {
                'predictions': predictions,
                'model_version': '1.1-enhanced',
                'message': f'Predições geradas para {len(book_features)} livros',
                'user_id': user_id,
                'total_books': len(predictions),
                'user_authenticated': current_user,
                'top_recommendation': predictions[0] if predictions else None
            }
            
            logger.info(f"Predições geradas com sucesso para {user_id}")
            return response_data, 200
            
        except Exception as e:
            logger.error(f"Erro no endpoint /ml/predictions: {str(e)}", exc_info=True)
            return {
                'message': 'Erro interno ao processar predições',
                'error': str(e),
                'status': 'error'
            }, 500