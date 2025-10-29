import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import create_app
from app.models.book import db
from app.services.scraper import BookScraper
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_scraper():
    app = create_app()
    
    with app.app_context():
        try:
            logger.info("Starting book scraping...")
            
            scraper = BookScraper()
            books_data = scraper.scrape_all_books()
            
            logger.info(f"Scraped {len(books_data)} books")
            
            # Salva no banco de dados
            from app.models.book import Book
            
            for book_data in books_data:
                book = Book(**book_data)
                db.session.add(book)
            
            db.session.commit()
            logger.info("Books saved to database successfully")
            
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            db.session.rollback()

if __name__ == '__main__':
    run_scraper()