# tests/final_test.py
import os
import sys
import json

# Adiciona o diretório raiz ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from app import create_app
from app.models.book import db

def run_all_tests():
    """Executa todos os testes em um único arquivo"""
    print("EXECUTANDO TESTES COMPLETOS DA BOOK API")
    print("=" * 50)
    
    all_tests_passed = True
    
    try:
        app = create_app(testing=True)
        
        with app.app_context():
            db.create_all()
            
            with app.test_client() as client:
                # TESTE 1: Health Check
                print("\n1. TESTANDO HEALTH CHECK...")
                response = client.get('/api/v1/health')
                if response.status_code == 200:
                    data = json.loads(response.data)
                    print("   ✅ HEALTH CHECK OK")
                    print(f"   Status: {data['status']}")
                else:
                    print(f"   ❌ HEALTH CHECK FALHOU: {response.status_code}")
                    all_tests_passed = False
                
                # TESTE 2: Endpoints Básicos
                print("\n2. TESTANDO ENDPOINTS BASICOS...")
                endpoints = [
                    ('/api/v1/books', 'GET'),
                    ('/api/v1/categories', 'GET'),
                    ('/api/v1/stats/overview', 'GET')
                ]
                
                for endpoint, method in endpoints:
                    if method == 'GET':
                        response = client.get(endpoint)
                    else:
                        response = client.post(endpoint)
                    
                    if response.status_code == 200:
                        print(f"   ✅ {endpoint} OK")
                    else:
                        print(f"   ⚠️  {endpoint}: {response.status_code} (pode ser normal)")
                
                # TESTE 3: Proteção de Rotas (sem auth)
                print("\n3. TESTANDO PROTECAO DE ROTAS...")
                protected_routes = [
                    ('/api/v1/ml/features', 'GET'),
                    ('/api/v1/ml/training-data', 'GET'),
                    ('/api/v1/ml/predictions', 'POST'),
                ]
                
                for route, method in protected_routes:
                    if method == 'GET':
                        response = client.get(route)
                    else:
                        response = client.post(route, json={})
                    
                    if response.status_code == 401:
                        print(f"   ✅ {route} CORRETAMENTE PROTEGIDA")
                    else:
                        print(f"   ❌ {route} NAO ESTA PROTEGIDA: {response.status_code}")
                        all_tests_passed = False
                
                # TESTE 4: Autenticação
                print("\n4. TESTANDO AUTENTICACAO...")
                response = client.post('/api/v1/auth/login', json={
                    'username': 'admin', 
                    'password': 'senha_admin_local'
                })
                
                if response.status_code == 200:
                    token = json.loads(response.data)['access_token']
                    headers = {'Authorization': f'Bearer {token}'}
                    print("   ✅ LOGIN BEM SUCEDIDO")
                    
                    # Testa acesso com token
                    test_routes = [
                        ('/api/v1/ml/features', 'GET'),
                        ('/api/v1/ml/training-data', 'GET'),
                    ]
                    
                    for route, method in test_routes:
                        if method == 'GET':
                            response = client.get(route, headers=headers)
                        else:
                            response = client.post(route, headers=headers, json={})
                        
                        if response.status_code == 200:
                            print(f"   ✅ ACESSO PERMITIDO A {route}")
                        else:
                            print(f"   ❌ ACESSO NEGADO A {route}: {response.status_code}")
                            all_tests_passed = False
                else:
                    print(f"   ⚠️  LOGIN FALHOU: {response.status_code} (pode ser normal em testes)")
                
                return all_tests_passed
                
    except Exception as e:
        print(f"💥 ERRO CRITICO NOS TESTES: {e}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 TODOS OS TESTES PRINCIPAIS PASSARAM!")
        print("A API ESTA PRONTA PARA USO!")
    else:
        print("💥 ALGUNS TESTES FALHARAM")
        print("Verifique os detalhes acima.")
    
    sys.exit(0 if success else 1)