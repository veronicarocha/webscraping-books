from dotenv import load_dotenv
load_dotenv()
import os
import time
from app import create_app, db
from config import Config

app = create_app()

with app.app_context():
    db.create_all()
    print(">>> Tabelas criadas")

    from app.models.book import Book
    from app.services.scraper import BookScraper
    
    book_count = Book.query.count()
    
    # CORREÇÃO: Cálculo correto do offset de categorias
    if book_count > 0:
        categories_count = db.session.query(Book.category).distinct().count()
    else:
        categories_count = 0  # Quando não há livros, offset é 0
    
    print(f">>>  Análise da Base:")
    print(f">>>  Livros: {book_count}")
    print(f">>>  Categorias: {categories_count}")
    
    TARGET_BOOKS = 1000  # Meta total
    MAX_TIME_MINUTES = 15  # Tempo máximo pra nao ficar em looping
    start_time = time.time()
    
    # Só executa se NÃO atingiu a meta
    if book_count < TARGET_BOOKS:
        print(f">>> INICIANDO SCRAPING INTELIGENTE")
        print(f">>>   Meta: {TARGET_BOOKS} livros")
        print(f">>>   Limite: {MAX_TIME_MINUTES} minutos")
        print(f">>>   Offset: {categories_count} categorias")
        
        try:
            scraper = BookScraper()
            all_categories = scraper.get_categories()
            
            # CORREÇÃO: Offset corrigido - agora pega todas as categorias quando categories_count = 0
            categories_to_process = dict(list(all_categories.items())[categories_count:])
            print(f">>>    📂 Categorias para processar: {len(categories_to_process)}/{len(all_categories)}")
            
            total_added = 0
            processed_in_this_run = 0
            
            for i, (category_name, category_url) in enumerate(categories_to_process.items(), categories_count + 1):
                # VERIFICAÇÃO DE TEMPO
                elapsed_minutes = (time.time() - start_time) / 60
                if elapsed_minutes >= MAX_TIME_MINUTES:
                    print(f">>> LIMITE DE {MAX_TIME_MINUTES} MINUTOS ATINGIDO")
                    break
                
                # VERIFICAÇÃO DE META
                current_count = Book.query.count()
                if current_count >= TARGET_BOOKS:
                    print(f">>> META DE {TARGET_BOOKS} LIVROS ATINGIDA")
                    break
                
                print(f">>> [{i}/{len(all_categories)}] Processando: {category_name}")
                print(f">>>    Tempo: {elapsed_minutes:.1f}min | Livros: {current_count}/{TARGET_BOOKS}")
                
                try:
                    category_books = scraper.scrape_single_category(category_name, category_url)
                    
                    category_added = 0
                    category_existing = 0
                    
                    for book_data in category_books:
                        if not Book.query.filter_by(title=book_data['title'], category=category_name).first():
                            book = Book(**book_data)
                            db.session.add(book)
                            category_added += 1
                        else:
                            category_existing += 1
                    
                    db.session.commit()
                    
                    total_added += category_added
                    processed_in_this_run += 1
                    
                    print(f">>> {category_name}: +{category_added} novos,{category_existing} existentes")
                    
                    # pausa
                    time.sleep(1)
                    
                except Exception as e:
                    print(f">>> Erro em {category_name}: {e}")
                    db.session.rollback()
                    continue
            
            # RELATÓRIO FINAL
            final_count = Book.query.count()
            final_categories = db.session.query(Book.category).distinct().count()
            elapsed_minutes = (time.time() - start_time) / 60
            
            print(f">>> SCRAPING CONCLUÍDO!")
            print(f">>>    Tempo total: {elapsed_minutes:.1f} minutos")
            print(f">>>    Categorias processadas: {processed_in_this_run}")
            print(f">>>    Livros adicionados: {total_added}")
            print(f">>>    Total na base: {final_count}/{TARGET_BOOKS}")
            print(f">>>    Categorias totais: {final_categories}")
            
            if final_count < TARGET_BOOKS:
                remaining = TARGET_BOOKS - final_count
                print(f">>> Faltam {remaining} livros - próximo deploy continuará automaticamente")
            
        except Exception as e:
            print(f">>> Erro no scraping inteligente: {e}")
    
    else:
        print(f">>> Meta atingida: {book_count}/{TARGET_BOOKS} livros")
        print(f">>> Base completa - Scraping não necessário")

if __name__ == '__main__':
    print(f">>> Iniciando Book API")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)