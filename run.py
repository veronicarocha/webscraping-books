from dotenv import load_dotenv
load_dotenv()
import os
import time
from app import create_app, db
from config import Config

app = create_app()

with app.app_context():
    db.create_all()
    print(">>> ✅ Tabelas criadas - VERIFICANDO SCRAPING AUTOMÁTICO")

    from app.models.book import Book
    from app.services.scraper import BookScraper
    
    book_count = Book.query.count()
    print(f">>> Livros na base: {book_count}")
    
    if book_count < 300:
        print(">>> 🚀 Iniciando scraping automático (MODO RÁPIDO - SEM ATUALIZAÇÃO)...")
        
        try:
            scraper = BookScraper()
            
            # Pega as categorias
            categories = scraper.get_categories()
            print(f">>> 📂 Encontradas {len(categories)} categorias")
            
            total_added = 0
            total_existing = 0
            processed_categories = 0
            
            for i, (category_name, category_url) in enumerate(categories.items(), 1):
                if processed_categories >= 8:  # ⬇Limite menor para evitar timeout
                    print(f">>> ⏹️  Limite de segurança: {processed_categories} categorias processadas")
                    break
                    
                print(f">>>  [{i}/{len(categories)}] Processando: {category_name}")
                
                try:
                    # Scraping apenas desta categoria
                    category_books = scraper.scrape_single_category(category_name, category_url)
                    
                    if not category_books:
                        print(f">>>   ⏩ {category_name}: Nenhum livro - pulando")
                        continue
                    
                    category_added = 0
                    category_existing = 0
                    
                    for book_data in category_books:
                        try:
                            # Busca livro existente
                            existing_book = Book.query.filter_by(
                                title=book_data['title'],
                                category=book_data['category']
                            ).first()
                            
                            if existing_book:
                                # LIVRO JÁ EXISTE - NÃO ATUALIZA!
                                category_existing += 1
                            else:
                                # ADICIONA NOVO livro
                                book = Book(**book_data)
                                db.session.add(book)
                                category_added += 1
                                
                        except Exception as e:
                            print(f">>>    Erro no livro: {e}")
                            continue
                    
                    # COMMIT APÓS CADA CATEGORIA
                    db.session.commit()
                    
                    total_added += category_added
                    total_existing += category_existing
                    processed_categories += 1
                    
                    print(f">>>   ✅ {category_name}: +{category_added} novos, ⏩{category_existing} existentes (pulados)")
                    
                    # PAUSA MENOR
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f">>>  Erro na categoria {category_name}: {e}")
                    db.session.rollback()
                    continue
            
            final_count = Book.query.count()
            print(f">>> SCRAPING RÁPIDO COMPLETO!")
            print(f">>> Categorias processadas: {processed_categories}/{len(categories)}")
            print(f">>> NOVOS livros: {total_added}")
            print(f">>> Existente (pulados): {total_existing}")
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