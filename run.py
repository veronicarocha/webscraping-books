from dotenv import load_dotenv
load_dotenv()

import os
from app import create_app, db
from config import Config

app = create_app()

with app.app_context():
    db.create_all()
    print(">>> Tabelas do banco criadas/verificadas!")
    
    # adicionando para o scraping aconter direto no deploy 
    from app.models.book import Book
    book_count = Book.query.count()
    print(f">>> Livros no banco: {book_count}")
    
    if book_count == 0:
        print(">>> 🚀 Executando scraper")
        try:
            from app.services.scraper import BookScraper
            scraper = BookScraper()
            
            books_data = scraper.get_all_books()
            
            print(f">>> {len(books_data)} livros coletados")
            
            # Salvando em lotes para não sobrecarregar
            batch_size = 50
            for i in range(0, len(books_data), batch_size):
                batch = books_data[i:i + batch_size]
                for book_data in batch:
                    book = Book(
                        title=book_data['title'],
                        price=book_data['price'],
                        rating=book_data['rating'],
                        availability=book_data['availability'],
                        category=book_data['category'],
                        image_url=book_data.get('image_url', ''),
                        description=book_data['description']
                    )
                    db.session.add(book)
                
                db.session.commit()
                print(f">>>  Lote {i//batch_size + 1} salvo: {i + len(batch)}/{len(books_data)}")
            
            final_count = Book.query.count()
            print(f">>> OK SCRAPER COMPLETO: {final_count} livros salvos no banco!")
            
        except Exception as e:
            print(f">>> NOK Erro no scraper: {str(e)}")
    else:
        print(f">>> Banco já populado com {book_count} livros")

if __name__ == '__main__':
    print(f">>> Iniciando Book API em modo: {Config.check_environment()}")
    port = int(os.environ.get('PORT', 5000))
    debug = Config.check_environment() == "desenvolvimento"
    app.run(host='0.0.0.0', port=port, debug=debug)