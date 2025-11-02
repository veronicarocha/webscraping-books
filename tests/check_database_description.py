# check_database_descriptions.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.book import db
from app.models.book import Book

def check_database():
    print("🔍 VERIFICANDO DESCRIÇÕES NA BASE DE DADOS")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        # Conta descrições
        total_books = Book.query.count()
        books_with_desc = Book.query.filter(
            Book.description != "No description available",
            Book.description != "Description not available", 
            Book.description != "Descrição não disponível no momento."
        ).count()
        
        books_no_desc = total_books - books_with_desc
        
        print(f"📊 TOTAL DE LIVROS: {total_books}")
        print(f"✅ COM descrição real: {books_with_desc}")
        print(f"❌ SEM descrição: {books_no_desc}")
        
        # Mostra alguns exemplos
        print(f"\n📝 EXEMPLOS NA BASE:")
        books = Book.query.limit(5).all()
        for i, book in enumerate(books):
            print(f"   {i+1}. {book.title[:50]}...")
            print(f"      Descrição: '{book.description}'")
            print(f"      Tamanho: {len(book.description)} chars")
            print()
        
        # Verifica se há algum com descrição real
        real_desc_books = Book.query.filter(
            Book.description != "No description available",
            Book.description != "Description not available",
            Book.description != "Descrição não disponível no momento.",
            Book.description != ""
        ).limit(3).all()
        
        if real_desc_books:
            print(f"🎯 LIVROS COM DESCRIÇÃO REAL:")
            for book in real_desc_books:
                print(f"   - {book.title}")
                print(f"     '{book.description[:100]}...'")
        else:
            print("❌ NENHUM LIVRO COM DESCRIÇÃO REAL ENCONTRADO")

if __name__ == "__main__":
    check_database()