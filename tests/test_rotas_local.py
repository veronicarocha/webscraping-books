import requests
import json

BASE_URL = "http://localhost:5000/api/v1"

def test_final():
    print("🎯 TESTE FINAL - API com PostgreSQL")
    
    endpoints = [
        "/health",
        "/books?per_page=3", 
        "/categories",
        "/stats/overview",
        "/books/top-rated?limit=3",
        "/stats/categories"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"✅ {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if 'books' in data:
                    print(f"   📚 {len(data['books'])} livros")
                elif 'categories' in data:
                    print(f"   🏷️  {len(data['categories'])} categorias")
                elif 'total_books' in data:
                    print(f"   📊 {data['total_books']} livros totais")
                    
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
    
    print(f"\n📖 Documentação: http://localhost:5000/apidocs/")

if __name__ == '__main__':
    test_final()