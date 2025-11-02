from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flasgger import Swagger
from app.models.book import db
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.config['JSON_AS_ASCII'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    
    # Inicializa extensões
    db.init_app(app)
    jwt = JWTManager(app)
    CORS(app)
    
    # registrar os comandos CLI
    from app.commands import register_commands
    register_commands(app)

    from app.utils.monitoring import setup_monitoring
    setup_monitoring(app)

    swagger = Swagger(app, template={
        "swagger": "2.0",
        "info": {
            "title": "Book API",
            "description": "API pública para consulta e recomendação de livros",
            "version": "1.0.0",
            "contact": {
                "email": "vedarocha@gmail.com"
            }
        },
        "securityDefinitions": {
            "Bearer Auth": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header. Example: \"Authorization: Bearer {token}\""
            }
        }
    })
    
    # Configurar API DEPOIS do Swagger
    api = Api(app, prefix='/api/v1')
    
    # Registra rrotas
    from app.api.core.routes import HealthCheck, ScrapingTrigger
    from app.api.auth.routes import Login, RefreshToken
    from app.api.books.routes import Books, BookDetail, BookSearch
    from app.api.categories.routes import Categories, CategoryStats
    from app.api.stats.routes import StatsOverview, TopRatedBooks, PriceRangeBooks
    from app.api.ml.routes import MLFeatures, TrainingData, Predictions
    
    # Core endpoints
    api.add_resource(HealthCheck, '/health')
    api.add_resource(ScrapingTrigger, '/scraping/trigger')
    
    # Books endpoints
    api.add_resource(Books, '/books')
    api.add_resource(BookDetail, '/books/<int:id>')
    api.add_resource(BookSearch, '/books/search')
    
    # Categories endpoints
    api.add_resource(Categories, '/categories')
    api.add_resource(CategoryStats, '/stats/categories')
    
    # Stats endpoints
    api.add_resource(StatsOverview, '/stats/overview')
    api.add_resource(TopRatedBooks, '/books/top-rated')
    api.add_resource(PriceRangeBooks, '/books/price-range')
    
    # Auth endpoints
    api.add_resource(Login, '/auth/login')
    api.add_resource(RefreshToken, '/auth/refresh')
    
    # ML endpoints
    api.add_resource(MLFeatures, '/ml/features')
    api.add_resource(TrainingData, '/ml/training-data')
    api.add_resource(Predictions, '/ml/predictions')
    
    return app