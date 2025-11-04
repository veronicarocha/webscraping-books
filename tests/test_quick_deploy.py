import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_quick_deploy():
    """Teste rápido para verificar se a app inicia"""
    try:
        os.environ.setdefault('SECRET_KEY', 'test-key-deploy')
        os.environ.setdefault('JWT_SECRET_KEY', 'test-jwt-deploy')
        
        if os.environ.get('GITHUB_ACTIONS') == 'true':
            os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')
            os.environ.setdefault('DATABASE_URL_PUBLIC', 'sqlite:///:memory:')
        
        from app import create_app
        
        print("1. Criando app...")
        app = create_app()
        print(" App criada")
        
        print("2. Testando contexto...")
        with app.app_context():
            print("  Contexto OK")
            
        print("3. Teste de saúde básico...")
        with app.test_client() as client:
            response = client.get('/api/v1/health')
            print(f"  Health: {response.status_code}")
            
        return True
        
    except Exception as e:
        print(f" ERRO: {e}")
        return False

if __name__ == "__main__":
    success = test_quick_deploy()
    
    print("\n" + "=" * 40)
    if success:
        print(" API PRONTA PARA DEPLOY!")
        sys.exit(0)
    else:
        print(" VERIFIQUE OS PROBLEMAS ACIMA")
        sys.exit(1)