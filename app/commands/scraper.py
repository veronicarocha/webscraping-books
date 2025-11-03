import click
from flask.cli import with_appcontext
from app.services.scraper import BookScraper
from app.models.book import Book, db
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

@click.command('scrape-books')
@click.option('--max-categories', default=None, type=int, help='Limitar categorias para teste')
@click.option('--clean', is_flag=True, default=False, help='Limpar banco antes (modo desenvolvimento)')
@with_appcontext
def scrape_books_command(max_categories, clean):
    """Comando para popular o banco """
    try:
        logger.info("Iniciando scraping de livros...")
        
        scraper = BookScraper()
        books_data = scraper.get_all_books(max_categories=max_categories)
        
        if clean:
            # em dev Limpeza completa
            logger.info("Modo desenvolvimento - limpando banco...")
            deleted_count = Book.query.delete()
            added_count = 0
            
            for book_data in books_data:
                book = Book(**book_data)
                db.session.add(book)
                added_count += 1
            
            db.session.commit()
            logger.info(f"Desenvolvimento: {deleted_count} removidos, {added_count} adicionados")
            
        else:
            # prod - usando Upsert
            logger.info("Atualizando dados existentes...")
            updated_count = 0
            added_count = 0
            skipped_count = 0
            
            for i, book_data in enumerate(books_data):
                try:
                    # Busca livro existente (titulo + categoria como chave única)
                    existing_book = Book.query.filter_by(
                        title=book_data['title'],
                        category=book_data['category']
                    ).first()
                    
                    if existing_book:
                        # atualizar livro existente
                        existing_book.price = book_data['price']
                        existing_book.rating = book_data['rating']
                        existing_book.availability = book_data['availability']
                        existing_book.image_url = book_data.get('image_url', '')
                        existing_book.description = book_data['description']
                        updated_count += 1
                        
                        if i % 50 == 0:  # Log a cada 50 atualizações
                            logger.info(f" Progresso: {i}/{len(books_data)}...")
                            
                    else:
                        book = Book(**book_data)
                        db.session.add(book)
                        added_count += 1
                        
                except Exception as e:
                    skipped_count += 1
                    logger.warning(f"⚠️  Pulando livro {i}: {str(e)[:100]}")
                    continue
            
            db.session.commit()
            
            # Estatísticas 
            total_processed = len(books_data)
            success_rate = ((updated_count + added_count) / total_processed) * 100
            
            logger.info(f"""
                        SCRAPING PRODUÇÃO COMPLETO!
                        📊 Estatísticas:
                           •  Livros processados: {total_processed}
                           •  Novos livros: {added_count}
                           •  Livros atualizados: {updated_count}
                           •  Livros pulados: {skipped_count}
                           •  Taxa de sucesso: {success_rate:.1f}%
                           •  Total no banco: {Book.query.count()} livros
                        """)
            
    except Exception as e:
        db.session.rollback()
        logger.error(f" ERRO no scraping: {e}")
        raise click.ClickException(f"Scraping falhou: {e}")