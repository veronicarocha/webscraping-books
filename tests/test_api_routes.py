#!/usr/bin/env python3
"""
Script para validar todas as rotas da Book API
"""

import requests
import json
import time
import sys
from datetime import datetime

class APITester:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.results = []
        self.session = requests.Session()
        
    def print_status(self, endpoint, status_code, response_time, success=True, details=""):
        """Print colorido do status"""
        status_color = "🟢" if success else "🔴"
        time_color = "⚡" if response_time < 500 else "🐢" if response_time < 2000 else "🚨"
        
        print(f"{status_color} {endpoint:40} | Status: {status_code:3} | Tempo: {response_time:6.2f}ms {time_color} {details}")
        
        self.results.append({
            'endpoint': endpoint,
            'status_code': status_code,
            'response_time': response_time,
            'success': success,
            'details': details
        })
    
    def test_endpoint(self, method, path, name=None, expected_status=200, **kwargs):
        """Testa um endpoint individual"""
        url = f"{self.base_url}{path}"
        endpoint_name = name or path
        
        try:
            start_time = time.time()
            response = self.session.request(method, url, timeout=10, **kwargs)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # ms
            
            success = response.status_code == expected_status
            details = ""
            
            if not success:
                details = f"Esperado: {expected_status}, Recebido: {response.status_code}"
                try:
                    error_data = response.json()
                    details += f" | Erro: {error_data.get('error', 'Unknown')}"
                except:
                    details += f" | Response: {response.text[:100]}"
            
            self.print_status(endpoint_name, response.status_code, response_time, success, details)
            
            return response
            
        except requests.exceptions.RequestException as e:
            response_time = 0
            self.print_status(endpoint_name, 0, response_time, False, f"Erro de conexão: {str(e)}")
            return None
    
    def test_health_check(self):
        """Testa health check"""
        print("\n🧪 TESTANDO HEALTH CHECK")
        print("=" * 80)
        
        self.test_endpoint('GET', '/api/v1/health', 'Health Check')
    
    def test_books_endpoints(self):
        """Testa endpoints de livros"""
        print("\n📚 TESTANDO ENDPOINTS DE LIVROS")
        print("=" * 80)
        
        # Listar livros
        response = self.test_endpoint('GET', '/api/v1/books?per_page=5', 'Listar Livros (5)')
        
        # Buscar livro específico se existirem livros
        if response and response.status_code == 200:
            books_data = response.json()
            if books_data.get('books') and len(books_data['books']) > 0:
                book_id = books_data['books'][0]['id']
                self.test_endpoint('GET', f'/api/v1/books/{book_id}', f'Detalhe Livro ID {book_id}')
        
        # Busca
        self.test_endpoint('GET', '/api/v1/books/search?q=python', 'Buscar Livros "python"')
        self.test_endpoint('GET', '/api/v1/books/top-rated', 'Top Rated Books')
        self.test_endpoint('GET', '/api/v1/books/price-range', 'Price Range Books')
    
    def test_categories_endpoints(self):
        """Testa endpoints de categorias"""
        print("\n🏷️ TESTANDO ENDPOINTS DE CATEGORIAS")
        print("=" * 80)
        
        self.test_endpoint('GET', '/api/v1/categories', 'Listar Categorias')
        self.test_endpoint('GET', '/api/v1/stats/categories', 'Estatísticas Categorias')
    
    def test_stats_endpoints(self):
        """Testa endpoints de estatísticas"""
        print("\n📊 TESTANDO ENDPOINTS DE ESTATÍSTICAS")
        print("=" * 80)
        
        self.test_endpoint('GET', '/api/v1/stats/overview', 'Overview Estatísticas')
    
    def test_ml_endpoints(self):
        """Testa endpoints de Machine Learning"""
        print("\n🤖 TESTANDO ENDPOINTS DE ML")
        print("=" * 80)
        
        self.test_endpoint('GET', '/api/v1/ml/features', 'ML Features')
        self.test_endpoint('GET', '/api/v1/ml/training-data', 'Training Data')
        self.test_endpoint('GET', '/api/v1/ml/predictions', 'Predictions')
    
    def test_auth_endpoints(self):
        """Testa endpoints de autenticação"""
        print("\n🔐 TESTANDO ENDPOINTS DE AUTENTICAÇÃO")
        print("=" * 80)
        
        # Login (deve falhar sem credenciais válidas)
        self.test_endpoint('POST', '/api/v1/auth/login', 'Login', 400)
        
        # Refresh token (deve falhar sem token)
        self.test_endpoint('POST', '/api/v1/auth/refresh', 'Refresh Token', 401)
    
    def test_debug_endpoints(self):
        """Testa endpoints de debug (nova rota)"""
        print("\n🐛 TESTANDO ENDPOINTS DE DEBUG")
        print("=" * 80)
        
        # Testa a nova rota de logs
        self.test_endpoint('GET', '/api/v1/debug/logs', 'Debug Logs (JSON)')
        self.test_endpoint('GET', '/api/v1/debug/logs?format=text', 'Debug Logs (Text)')
        self.test_endpoint('GET', '/api/v1/debug/logs?limit=10', 'Debug Logs (Limit 10)')
        self.test_endpoint('GET', '/api/v1/debug/logs?level=INFO', 'Debug Logs (Level INFO)')
    
    def test_scraping_endpoints(self):
        """Testa endpoints de scraping"""
        print("\n🔄 TESTANDO ENDPOINTS DE SCRAPING")
        print("=" * 80)
        
        # Scraping trigger (pode requerer autenticação)
        self.test_endpoint('POST', '/api/v1/scraping/trigger', 'Scraping Trigger', 401)
    
    def generate_report(self):
        """Gera relatório final"""
        print("\n" + "=" * 80)
        print("📋 RELATÓRIO FINAL")
        print("=" * 80)
        
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - successful_tests
        
        # Tempo médio de resposta
        avg_response_time = sum(r['response_time'] for r in self.results if r['response_time'] > 0) / total_tests
        
        print(f"📊 Total de testes: {total_tests}")
        print(f"✅ Sucessos: {successful_tests}")
        print(f"❌ Falhas: {failed_tests}")
        print(f"⚡ Tempo médio de resposta: {avg_response_time:.2f}ms")
        
        # Taxa de sucesso
        success_rate = (successful_tests / total_tests) * 100
        print(f"📈 Taxa de sucesso: {success_rate:.1f}%")
        
        # Endpoints com problemas
        if failed_tests > 0:
            print(f"\n🔴 ENDPOINTS COM PROBLEMAS:")
            for result in self.results:
                if not result['success']:
                    print(f"   • {result['endpoint']}: {result['details']}")
        
        # Performance
        slow_endpoints = [r for r in self.results if r['response_time'] > 1000]
        if slow_endpoints:
            print(f"\n🐢 ENDPOINTS LENTOS (>1000ms):")
            for result in slow_endpoints:
                print(f"   • {result['endpoint']}: {result['response_time']:.2f}ms")
        
        return successful_tests == total_tests
    
    def run_all_tests(self):
        """Executa todos os testes"""
        print(f"🚀 INICIANDO TESTES DA BOOK API")
        print(f"📍 URL Base: {self.base_url}")
        print(f"🕐 Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Executa todos os testes
        self.test_health_check()
        self.test_books_endpoints()
        self.test_categories_endpoints()
        self.test_stats_endpoints()
        self.test_ml_endpoints()
        self.test_auth_endpoints()
        self.test_debug_endpoints()
        self.test_scraping_endpoints()
        
        # Gera relatório
        all_passed = self.generate_report()
        
        return all_passed

def main():
    # Configuração da URL base
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        # Tenta detectar automaticamente
        if os.environ.get('RAILWAY_ENVIRONMENT'):
            base_url = "http://book-api:5000"
        else:
            base_url = "http://localhost:5000"
    
    print("🌐 Configurando teste para:", base_url)
    
    # Executa os testes
    tester = APITester(base_url)
    success = tester.run_all_tests()
    
    # Retorna código de saída apropriado
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    import os
    main()