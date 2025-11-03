from dotenv import load_dotenv
load_dotenv()
import os
import time
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
    
    if book_count < 1000:
        print(">>> Iniciando scraping automático (COMMIT POR CATEGORIA)...")
        
        try:
            scraper = BookScraper()
            
            # Pega as categorias
            categories = scraper.get_categories()
            print(f">>> 📂 Encontradas {len(categories)} categorias")
            
            total_added = 0
            total_updated = 0
            processed_categories = 0
            
            # Processa UMA categoria por vez, com COMMIT após cada
            for i, (category_name, category_url) in enumerate(categories.items(), 1):
                print(f">>> 🎯 [{i}/{len(categories)}] Processando: {category_name}")
                
                try:
                    # Scraping apenas desta categoria
                    category_books = scraper.scrape_single_category(category_name, category_url)
                    
                    if not category_books:
                        print(f">>>   ⏩ {category_name}: Nenhum livro - pulando")
                        continue
                    
                    # UPSERT dos livros desta categoria
                    category_added = 0
                    category_updated = 0
                    
                    for book_data in category_books:
                        try:
                            # Busca livro existente
                            existing_book = Book.query.filter_by(
                                title=book_data['title'],
                                category=book_data['category']
                            ).first()
                            
                            if existing_book:
                                # Atualiza
                                existing_book.price = book_data['price']
                                existing_book.rating = book_data['rating']
                                existing_book.availability = book_data['availability']
                                existing_book.image_url = book_data.get('image_url', '')
                                existing_book.description = book_data['description']
                                category_updated += 1
                            else:
                                # Adiciona novo
                                book = Book(**book_data)
                                db.session.add(book)
                                category_added += 1
                                
                        except Exception as e:
                            print(f">>>   ⚠️  Erro no livro: {e}")
                            continue
                    
                    # COMMIT APÓS CADA CATEGORIA
                    db.session.commit()
                    
                    total_added += category_added
                    total_updated += category_updated
                    processed_categories += 1
                    
                    print(f">>>   ✅ {category_name}: +{category_added} novos, ↗{category_updated} atualizados")
                    
                    # Pequena pausa entre categorias
                    time.sleep(1)
                    
                except Exception as e:
                    print(f">>>   Erro na categoria {category_name}: {e}")
                    db.session.rollback()  # Rollback apenas desta categoria
                    continue
            
            final_count = Book.query.count()
            print(f">>> SCRAPING INCREMENTAL COMPLETO!")
            print(f">>> Categorias processadas: {processed_categories}/{len(categories)}")
            print(f">>> Novos livros: {total_added}")
            print(f">>> Atualizados: {total_updated}")
            print(f">>> Total na base: {final_count}")
            
        except Exception as e:
            print(f">>> Erro no scraping automático: {e}")
    else:
        print(">>> Base já populada - Scraping automático ignorado")

if __name__ == '__main__':
    print(f">>> Iniciando Book API em modo: {Config.check_environment()}")
    port = int(os.environ.get('PORT', 5000))
    debug = Config.check_environment() == "desenvolvimento"
    app.run(host='0.0.0.0', port=port, debug=debug)