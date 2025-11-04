import os
import time
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # Sobe um nível: scripts/ e o webscraping-books/
sys.path.insert(0, project_root)

#config da url 
from app.utils.database import setup_database_environment
setup_database_environment()

from app import create_app, db
from app.models.book import Book
from app.services.scraper import BookScraper

app = create_app()

with app.app_context():
    book_count = Book.query.count()
    categories_count = db.session.query(Book.category).distinct().count()
    
    TARGET_BOOKS = 1000
    MAX_TIME_MINUTES = 15
    
    if book_count < TARGET_BOOKS:
        print(f"Completando: {book_count} → {TARGET_BOOKS} livros")
        
        scraper = BookScraper()
        categories = dict(list(scraper.get_categories().items())[categories_count:])
        
        start_time = time.time()
        total_added = 0
        
        for name, url in categories.items():
            if (time.time() - start_time) / 60 >= MAX_TIME_MINUTES:
                break
            if Book.query.count() >= TARGET_BOOKS:
                break
                
            books = scraper.scrape_single_category(name, url)
            added = sum(1 for book_data in books if not Book.query.filter_by(title=book_data['title'], category=name).first())
            
            for book_data in books:
                if not Book.query.filter_by(title=book_data['title'], category=name).first():
                    db.session.add(Book(**book_data))
            
            db.session.commit()
            total_added += added
            print(f"{name}: +{added}")
            
            time.sleep(1)
        
        print(f" Adicionados: {total_added} | Total: {Book.query.count()}")
    
    else:
        print(" Base já completa!")