import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import create_app, db
from app.models.book import Book
from app.services.scraper import BookScraper
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_scraper():
    app = create_app()
    
    with app.app_context():
        try:
            logger.info("🚀 Starting book scraping...")
            
            scraper = BookScraper()
            
            # Todo: max_categories=2 - para produção: max_categories=None
            books_data = scraper.get_all_books(max_categories=None)
            
            logger.info(f" Scraped {len(books_data)} books")
            
            logger.info(" Cleaning existing database...")
            Book.query.delete()
            db.session.commit()
            
            saved_count = 0
            error_count = 0
            
            for book_data in books_data:
                try:
                    if not book_data.get('title'):
                        error_count += 1
                        continue
                        
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
                    saved_count += 1
                    
                    # Commit a cada 50 livros para não sobrecarregar
                    if saved_count % 50 == 0:
                        db.session.commit()
                        logger.info(f" Saved {saved_count} books so far...")
                        
                except Exception as e:
                    error_count += 1
                    logger.error(f" Error saving book '{book_data.get('title', 'Unknown')}': {e}")
                    continue
            
            db.session.commit()
            
            # Estatísticas
            with_desc = Book.query.filter(
                Book.description != "Descrição não disponível", 
                Book.description != ""
            ).count()
            total_books = Book.query.count()
            
            logger.info("🎉 Books saved to database successfully!")
            logger.info(f"📈 Statistics:")
            logger.info(f"   📚 Total books in database: {total_books}")
            logger.info(f"   ✅ With description: {with_desc}")
            logger.info(f"   ❌ Without description: {total_books - with_desc}")
            logger.info(f"   📊 Success rate: {(with_desc/total_books)*100:.1f}%" if total_books > 0 else "N/A")
            logger.info(f"   ⚠️  Errors during save: {error_count}")
            
            # Mostra amostra dos dados salvos
            sample_books = Book.query.limit(3).all()
            logger.info(f"\n🔍 Sample of saved books:")
            for book in sample_books:
                has_desc = "✅" if book.description and book.description != "Descrição não disponível" else "❌"
                logger.info(f"   {has_desc} {book.title[:40]}...")
                logger.info(f"      💰 £{book.price} | ⭐ {book.rating}/5 | 📍 {book.category}")
            
        except Exception as e:
            logger.error(f"❌ Scraping failed: {e}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    run_scraper()