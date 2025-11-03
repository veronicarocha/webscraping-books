import os
import logging
import click
from flask.cli import with_appcontext
from app.models.book import Book, db
from app.services.scraper import BookScraper

logger = logging.getLogger(__name__)

@click.command('scrape-books')
@click.option('--max-categories', default=None, type=int, help='Limitar categorias para teste')
@click.option('--clean', is_flag=True, default=False, help='Limpar banco antes (só no RAILWAY)')
@click.option('--offset', default=0, type=int, help='Pular X primeiras categorias')
@with_appcontext
def scrape_books_command(max_categories, clean, offset):
    """Comando pra popular o banco - EXECUTAR APENAS NO RAILWAY"""
    try:
        if not os.environ.get('RAILWAY_ENVIRONMENT') and not os.environ.get('RAILWAY_SERVICE_NAME'):
            logger.error("ERRO: Scraping deve ser executado APENAS no ambiente Railway")
            logger.error(" Comando correto: railway run flask scrape-books")
            raise click.ClickException("Scraping bloqueado localmente - execute no Railway")
        
        logger.info("Ambiente Railway detectado - Iniciando scraping...")
        
        scraper = BookScraper()
        
        # OBTÉM CATEGORIAS COM OFFSET
        all_categories = scraper.get_categories()
        logger.info(f"📂 Total de categorias encontradas: {len(all_categories)}")
        
        # APLICA OFFSET - pula X primeiras categorias
        if offset > 0:
            categories_to_process = dict(list(all_categories.items())[offset:])
            logger.info(f"⏩ Pulando {offset} categorias, processando {len(categories_to_process)} restantes")
        else:
            categories_to_process = all_categories
        
        # APLICA MAX CATEGORIES - limita quantas processar
        if max_categories:
            categories_to_process = dict(list(categories_to_process.items())[:max_categories])
            logger.info(f"🔢 Limitando para {max_categories} categorias")
        
        logger.info(f"Processando {len(categories_to_process)} categorias...")
        
        if clean:
            logger.info("Modo limpeza - removendo todos os livros...")
            deleted_count = Book.query.delete()
            
            # Scraping completo das categorias selecionadas
            books_data = []
            for cat_name, cat_url in categories_to_process.items():
                cat_books = scraper.scrape_single_category(cat_name, cat_url)
                books_data.extend(cat_books)
            
            added_count = 0
            for book_data in books_data:
                book = Book(**book_data)
                db.session.add(book)
                added_count += 1
            
            db.session.commit()
            logger.info(f"✅ Limpeza completa: {deleted_count} removidos, {added_count} adicionados")
            
        else:
            total_added = 0
            total_existing = 0
            skipped_count = 0
            processed_categories = 0
            
            for i, (category_name, category_url) in enumerate(categories_to_process.items(), offset + 1):
                logger.info(f"📦 Processando categoria {i}/{len(all_categories)}: {category_name}")
                
                try:
                    # Scraping apenas desta categoria
                    category_books = scraper.scrape_single_category(category_name, category_url)
                    
                    if not category_books:
                        logger.info(f" {category_name}: Nenhum livro encontrado - pulando")
                        skipped_count += 1
                        continue
                    
                    category_added = 0
                    category_existing = 0
                    
                    for book_data in category_books:
                        try:
                            # Busca livro existente (titulo + categoria como chave única)
                            existing_book = Book.query.filter_by(
                                title=book_data['title'],
                                category=book_data['category']
                            ).first()
                            
                            if existing_book:
                                # LIVRO JÁ EXISTE - NÃO ATUALIZA, SÓ PULA
                                category_existing += 1
                            else:
                                # ADICIONA NOVO livro
                                book = Book(**book_data)
                                db.session.add(book)
                                category_added += 1
                                
                        except Exception as e:
                            skipped_count += 1
                            logger.warning(f"⚠️  Erro no livro: {str(e)[:100]}")
                            continue
                    
                    # COMMIT APÓS CADA CATEGORIA
                    db.session.commit()
                    
                    total_added += category_added
                    total_existing += category_existing
                    processed_categories += 1
                    
                    logger.info(f" {category_name}: +{category_added} novos, ⏩{category_existing} existentes (pulados)")
                    
                except Exception as e:
                    skipped_count += 1
                    logger.error(f" Erro na categoria {category_name}: {e}")
                    db.session.rollback()  # Rollback apenas desta categoria
                    continue
            
            # Estatísticas 
            total_books_processed = len(categories_to_process) * 20  # Estimativa
            success_rate = (total_added / total_books_processed) * 100 if total_books_processed > 0 else 0
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"ERRO no scraping: {e}")
        raise click.ClickException(f"Scraping falhou: {e}")