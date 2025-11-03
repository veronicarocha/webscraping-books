from dotenv import load_dotenv
load_dotenv()
import os
from app import create_app, db
from config import Config

app = create_app()

with app.app_context():
    db.create_all()
    print(">>> Tabelas criadas - VERIFICANDO SCRAPING AUTOMÁTICO")

    from app.models.book import Book
    from app.services.scraper import BookScraper
    
    book_count = Book.query.count()
    print(f">>> Livros na base: {book_count}")
    
    if book_count < 50:
        print(">>> 🚀 Iniciando scraping automático (modo UPSERT)...")
        
        try:
            scraper = BookScraper()
            books_data = scraper.get_all_books(max_categories=None)  
            
            added_count = 0
            updated_count = 0
            
            for book_data in books_data:
                try:
                    # Busca se livro já existe (UPSERT)
                    existing_book = Book.query.filter_by(
                        title=book_data['title'],
                        category=book_data['category']
                    ).first()
                    
                    if existing_book:
                        # Atualiza livro existente
                        existing_book.price = book_data['price']
                        existing_book.rating = book_data['rating']
                        existing_book.availability = book_data['availability']
                        existing_book.image_url = book_data.get('image_url', '')
                        existing_book.description = book_data['description']
                        updated_count += 1
                    else:
                        # Adiciona novo livro
                        book = Book(**book_data)
                        db.session.add(book)
                        added_count += 1
                        
                except Exception as e:
                    print(f">>> Erro no livro: {e}")
                    continue
            
            db.session.commit()
            
            final_count = Book.query.count()
            print(f">>> SCRAPING COMPLETO!")
            print(f">>>    Novos livros: {added_count}")
            print(f">>>    Atualizados: {updated_count}")
            print(f">>>    Total na base: {final_count}")
            
        except Exception as e:
            print(f">>> Erro no scraping automático: {e}")
            # NÃO quebra o deploy se o scraping falhar
    else:
        print(">>> Base já populada - Scraping automático ignorado")

if __name__ == '__main__':
    print(f">>> Iniciando Book API em modo: {Config.check_environment()}")
    port = int(os.environ.get('PORT', 5000))
    debug = Config.check_environment() == "desenvolvimento"
    app.run(host='0.0.0.0', port=port, debug=debug)