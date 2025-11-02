import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from app.models.book import db
from sqlalchemy import text  

def setup_database():
    app = create_app()
    
    with app.app_context():
        try:
            # Criar todas as tabelas
            db.create_all()
            print("✅ Tabelas criadas com sucesso!")
            
            # Testar conexão (CORRIGIDO)
            db.session.execute(text('SELECT 1'))
            print("✅ Conexão com PostgreSQL testada!")
            
            # Verificar se foi criado
            from app.models.book import Book
            book_count = Book.query.count()
            print(f"📊 Total de livros no banco: {book_count}")
            
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == '__main__':
    setup_database()