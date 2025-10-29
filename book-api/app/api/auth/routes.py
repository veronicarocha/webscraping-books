from flask import request
from flask_restful import Resource
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity
)
from flasgger import swag_from
import logging

from .models import USERS

logger = logging.getLogger(__name__)

class Login(Resource):
    @swag_from({
        'tags': ['Adicional_auth'],
        'parameters': [
            {
                'name': 'body',
                'in': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'username': {'type': 'string'},
                        'password': {'type': 'string'}
                    },
                    'required': ['username', 'password']
                }
            }
        ],
        'responses': {
            200: {
                'description': 'Login realizado com sucesso'
            },
            401: {
                'description': 'Credenciais inválidas'
            }
        }
    })
    def post(self):
        """Obter token JWT"""
        try:
            username = None
            password = None
            
            if request.is_json:
                data = request.get_json()
                username = data.get('username')
                password = data.get('password')
            elif request.form:
                username = request.form.get('username')
                password = request.form.get('password')
            else:
                try:
                    data = request.get_json(force=True, silent=True)
                    if data:
                        username = data.get('username')
                        password = data.get('password')
                except:
                    pass
            
            if not username or not password:
                username = request.args.get('username')
                password = request.args.get('password')
            
            if not username or not password:
                return {
                    'error': 'Usuário e Senha obrigatórios',
                    'received_content_type': request.content_type
                }, 400
            
            user = USERS.get(username)
            if user and user['password'] == password:
                user_identity = f"{username}:{user['role']}"
                
                access_token = create_access_token(identity=user_identity)
                refresh_token = create_refresh_token(identity=user_identity)
                
                logger.info(f"User {username} logged in successfully")
                
                return {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'role': user['role'],
                    'username': username
                }, 200
            
            logger.warning(f"Failed login attempt for user: {username}")
            return {'error': 'Credenciais Invalidas'}, 401
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return {'error': 'Erro interno no servidor'}, 500

class RefreshToken(Resource):
    @jwt_required(refresh=True)
    @swag_from({
        'tags': ['Adicional_auth'],
        'security': [{'Bearer Auth': []}],
        'responses': {
            200: {
                'description': 'Token renovado com sucesso'
            }
        }
    })
    def post(self):
        """Renovar token de acesso usando refresh token"""
        try:
            current_user = get_jwt_identity()  
            new_token = create_access_token(identity=current_user)
            
            logger.info(f"Token refreshed for user: {current_user}")
            
            return {
                'access_token': new_token
            }, 200
            
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return {'error': 'Erro interno no servidor'}, 500