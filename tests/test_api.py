import os
import sys
import json

# Adiciona o path do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_api_with_test_client():
    """Testa a API usando o test client do Flask"""
    print("=" * 50)
    
    try:
        os.environ.setdefault('SECRET_KEY', 'test-secret-key')
        os.environ.setdefault('JWT_SECRET_KEY', 'test-jwt-key')
        os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')
        os.environ.setdefault('DATABASE_URL_PUBLIC', 'sqlite:///:memory:')
        
        from app import create_app
        
        app = create_app()
        
        with app.test_client() as client:
            # Teste 1: Health Check
            print("1. Health Check...")
            response = client.get('/api/v1/health')
            status = response.status_code
            print(f"   ✅ /health: {status}")
            
            # Teste 2: Listar livros
            print("2. Endpoint de livros...")
            response = client.get('/api/v1/books?per_page=3')
            status = response.status_code
            if status == 200:
                data = json.loads(response.data)
                book_count = len(data.get('books', []))
                print(f"   /books: {status} ({book_count} livros)")
            else:
                print(f"   /books: {status}")
            
            # Teste 3: Categorias
            print("3. Endpoint de categorias...")
            response = client.get('/api/v1/categories')
            status = response.status_code
            if status == 200:
                data = json.loads(response.data)
                cat_count = len(data.get('categories', []))
                print(f"   /categories: {status} ({cat_count} categorias)")
            else:
                print(f"   /categories: {status}")
            
            # Teste 4: Stats
            print("4. Endpoint de estatísticas...")
            response = client.get('/api/v1/stats/overview')
            status = response.status_code
            print(f"   /stats/overview: {status}")
            
            # Teste 5: Top rated
            print("5. Endpoint top rated...")
            response = client.get('/api/v1/books/top-rated?limit=3')
            status = response.status_code
            print(f"   /books/top-rated: {status}")
            
            print("=" * 50)
            print("Todos os endpoints responderam!")
            return True
            
    except Exception as e:
        print(f" ERRO: {e}")
        return False

if __name__ == '__main__':
    success = test_api_with_test_client()
    sys.exit(0 if success else 1)