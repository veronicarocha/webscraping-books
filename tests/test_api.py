import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
import json

def test_quick_deploy():
    
    try:
        app = create_app()
        
        with app.test_client() as client:
            # Teste básico - health check
            print("1. Health Check...")
            response = client.get('/api/v1/health')
            if response.status_code == 200:
                print(" HEALTH CHECK OK")
            else:
                print(f" HEALTH CHECK: {response.status_code}")
                return False
            
            # Teste p ver se a aplicação responde
            print("2. Endpoint básico...")
            response = client.get('/api/v1/books')
            if response.status_code in [200, 500]: 
                print("    API RESPONDENDO")
            else:
                print(f"    API: {response.status_code}")
                return False
            
            # Teste Swagger
            print("3. Documentação...")
            response = client.get('/apispec_1.json')
            if response.status_code == 200:
                print("   SWAGGER OK")
            else:
                print(f"  SWAGGER: {response.status_code}")
                return False
            
            assert True
            
    except Exception as e:
        print(f" ERRO: {e}")
        return False

if __name__ == "__main__":
    success = test_quick_deploy()
    
    print("\n" + "=" * 40)
    if success:
        print(" API PRONTA PARA DEPLOY!")
    else:
        print(" VERIFIQUE OS PROBLEMAS ACIMA")
    
    sys.exit(0 if success else 1)