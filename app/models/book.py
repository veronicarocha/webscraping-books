from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON

db = SQLAlchemy()

class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    price = db.Column(db.Float, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    availability = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(500))
    description = db.Column(db.Text)
    scraped_at = db.Column(db.DateTime, server_default=db.func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'price': self.price,
            'rating': self.rating,
            'availability': self.availability,
            'category': self.category,
            'image_url': self.image_url,
            'description': self.description
        }