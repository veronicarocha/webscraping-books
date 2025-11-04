import time
import sys
import os
from datetime import datetime
from collections import defaultdict
import logging

# CORREÇÃO: Adiciona o diretório raiz ao path ANTES de importar o app
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # Sobe um nível: scripts/ e webscraping-books/
sys.path.insert(0, project_root)

from app.utils.database import setup_database_environment
setup_database_environment()

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ScrapingReconciliation:
    def __init__(self, scraper, db_session):
        self.scraper = scraper
        self.db_session = db_session
        self.discrepancies = []
        
    def analisar_conciliação(self):
        logger.info("Iniciando analise de conciliacao")
        
        categorias_base = self._get_categorias_da_base()
        livros_por_categoria_base = self._get_contagem_livros_por_categoria()
        
        categorias_site = self.scraper.get_categories()
        
        # Obtém dados dos livros do site
        livros_por_categoria_site, livros_detalhados_site = self._get_livros_detalhados_site(categorias_site)
        
        self._mostrar_comparacao_completa(livros_por_categoria_base, livros_por_categoria_site)
        
        # CORREÇÃO: Análise que inclui TODAS as categorias do site
        self._analisar_discrepancias_completas(
            categorias_base, 
            categorias_site,
            livros_por_categoria_base,
            livros_por_categoria_site,
            livros_detalhados_site
        )
        
        return self.discrepancies

    def _get_livros_detalhados_site(self, categorias_site):
        """Obtém dados COMPLETOS dos livros do site (com URLs)"""
        livros_por_categoria_site = {}
        livros_detalhados_site = defaultdict(list)
        
        logger.info("OBTENDO DADOS DETALHADOS DO SITE...")
        
        for categoria_nome, categoria_url in categorias_site.items():
            try:
                livros_categoria = self._scrape_categoria_com_urls(categoria_nome, categoria_url)
                livros_detalhados_site[categoria_nome] = livros_categoria
                livros_por_categoria_site[categoria_nome] = len(livros_categoria)
                
                # Verifica edições diferentes
                edicoes_diferentes = self._encontrar_edicoes_diferentes(livros_categoria)
                if edicoes_diferentes:
                    logger.info(f"   📚 {categoria_nome}: {len(edicoes_diferentes)} títulos com edições diferentes:")
                    for titulo, edicoes in edicoes_diferentes.items():
                        logger.info(f"      • '{titulo}': {len(edicoes)} edições")
                
                logger.info(f"   ✅ {categoria_nome}: {len(livros_categoria)} livros")
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Erro ao obter livros de '{categoria_nome}': {e}")
                livros_por_categoria_site[categoria_nome] = 0
                
        return livros_por_categoria_site, livros_detalhados_site

    def _encontrar_edicoes_diferentes(self, livros):
        """Encontra livros com mesmo título mas preços/ratings diferentes"""
        from collections import defaultdict
        livros_por_titulo = defaultdict(list)

        for livro in livros:
            titulo = livro['title']
            livros_por_titulo[titulo].append({
                'price': livro['price'],
                'rating': livro['rating'],
                'availability': livro['availability']
            })

        edicoes_diferentes = {}
        for titulo, edicoes in livros_por_titulo.items():
            if len(edicoes) > 1:
                # Verifica se há diferenças reais (preço, rating, etc)
                preços = [ed['price'] for ed in edicoes]
                ratings = [ed['rating'] for ed in edicoes]

                if len(set(preços)) > 1 or len(set(ratings)) > 1:
                    edicoes_diferentes[titulo] = edicoes
    
        return edicoes_diferentes

    def _scrape_categoria_com_urls(self, categoria_nome, categoria_url):
        """Scraping que retorna livros com URLs únicas"""
        livros_detalhados = []
        page_url = categoria_url
        
        try:
            while page_url:
                response = self.scraper.session.get(page_url, headers=self.scraper.headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                books_elements = soup.select('article.product_pod')
                
                for book_element in books_elements:
                    livro_data = self._extrair_livro_com_url(book_element, categoria_nome)
                    if livro_data:
                        livros_detalhados.append(livro_data)
                
                # Verifica próxima página
                next_button = soup.select_one('li.next a')
                if next_button:
                    page_url = urljoin(page_url, next_button['href'])
                else:
                    page_url = None
                
                time.sleep(0.5)
                    
        except Exception as e:
            logger.error(f"Erro no scraping detalhado de {categoria_nome}: {e}")
        
        return livros_detalhados

    def _extrair_livro_com_url(self, book_element, categoria_nome):
        """Extrai livro usando apenas campos válidos do modelo Book"""
        try:
            book_link = book_element.select_one('h3 a')
            if not book_link:
                return None

            # Corrige URL 
            book_relative_url = book_link['href']
            while book_relative_url.startswith('../'):
                book_relative_url = book_relative_url[3:]

            if not book_relative_url.startswith('catalogue/'):
                book_relative_url = f'catalogue/{book_relative_url}'

            book_url = urljoin(self.scraper.base_url, book_relative_url)

            # Extrai ID único da URL (apenas para comparação interna)
            url_parts = urlparse(book_url)
            path_parts = url_parts.path.split('/')
            livro_id = path_parts[-2] if path_parts[-1] == '' else path_parts[-1]
            livro_id = livro_id.replace('.html', '')

            # Informações básicas 
            title = book_link.get('title', '').strip()

            # Preço
            price_element = book_element.select_one('.price_color')
            price_text = price_element.get_text(strip=True) if price_element else "£0.00"
            try:
                price = float(price_text.replace('£', ''))
            except:
                price = 0.0

            # Disponibilidade
            availability = book_element.select_one('.instock.availability')
            availability = availability.get_text(strip=True) if availability else "Out of stock"

            # Rating
            rating_element = book_element.select_one('p.star-rating')
            rating = 0
            if rating_element:
                rating_classes = rating_element.get('class', [])
                for cls in rating_classes:
                    if cls.startswith('One'): rating = 1
                    elif cls.startswith('Two'): rating = 2
                    elif cls.startswith('Three'): rating = 3
                    elif cls.startswith('Four'): rating = 4
                    elif cls.startswith('Five'): rating = 5

            # Imagem
            image_element = book_element.select_one('img')
            image_url = ""
            if image_element and image_element.get('src'):
                image_relative_url = image_element['src']
                while image_relative_url.startswith('../'):
                    image_relative_url = image_relative_url[3:]
                if not image_relative_url.startswith('catalogue/'):
                    image_relative_url = f'catalogue/{image_relative_url}'
                image_url = urljoin(self.scraper.base_url, image_relative_url)

            return {
                'title': title,
                'price': price,
                'availability': availability,
                'rating': rating,
                'description': "A ser coletada no salvamento",
                'category': categoria_nome,
                'image_url': image_url,
                '_internal_url': book_url,
                '_internal_url_id': livro_id,
                '_internal_chave_unica': f"{title}||{livro_id}||{price}||{rating}"
            }

        except Exception as e:
            logger.error(f"Erro ao extrair livro detalhado: {e}")
            return None

    def _mostrar_comparacao_completa(self, base_counts, site_counts):
        """Mostra comparação lado a lado entre base e site"""
        logger.info("📊 COMPARAÇÃO COMPLETA BASE vs SITE")
        logger.info("=" * 60)
        logger.info("CATEGORIA".ljust(25) + "BASE".rjust(8) + "SITE".rjust(8) + "STATUS".rjust(10))
        logger.info("-" * 60)
        
        todas_categorias = set(list(base_counts.keys()) + list(site_counts.keys()))
        
        for categoria in sorted(todas_categorias):
            base = base_counts.get(categoria, 0)
            site = site_counts.get(categoria, 0)
            
            status = "✅ OK"
            if base == 0 and site > 0:
                status = "❌ FALTANTE"
            elif site == 0 and base > 0:
                status = "⚠️  INATIVA"
            elif base < site:
                status = f"📉 -{site-base}"
            elif base > site:
                status = f"📈 +{base-site}"
                
            logger.info(f"{categoria.ljust(25)}{str(base).rjust(8)}{str(site).rjust(8)}{status.rjust(10)}")
        
        logger.info("=" * 60)

    def _get_categorias_da_base(self):
        from app.models.book import Book
        
        try:
            livros = Book.query.all()
            categorias_set = set()
            for livro in livros:
                if livro.category:
                    categoria_normalizada = livro.category.strip()
                    categorias_set.add(categoria_normalizada)
            categorias_base = list(categorias_set)
                
            logger.info(f"Base: {len(categorias_base)} categorias encontradas")
            return categorias_base
        except Exception as e:
            logger.error(f"Erro ao buscar categorias da base: {e}")
            return []
    
    def _get_contagem_livros_por_categoria(self):
        from app.models.book import Book
        
        try:
            livros_por_categoria = defaultdict(int)
            livros = Book.query.all()
            
            for livro in livros:
                if livro.category:
                    categoria_normalizada = livro.category.strip()
                    livros_por_categoria[categoria_normalizada] += 1
                    
            logger.info(f"Base: {len(livros)} livros distribuidos em {len(livros_por_categoria)} categorias")
            return livros_por_categoria
        except Exception as e:
            logger.error(f"Erro ao contar livros por categoria: {e}")
            return defaultdict(int)

    def _analisar_discrepancias_completas(self, categorias_base, categorias_site, base_counts, site_counts, livros_detalhados_site):
        """ANÁLISE COMPLETA: Inclui TODAS as categorias do site - CORRIGIDO"""
        
        # CORREÇÃO: Processa TODAS as categorias do site, não só as que estão na base
        todas_categorias = set(list(categorias_base) + list(categorias_site.keys()))
        
        for categoria in sorted(todas_categorias):
            if categoria not in site_counts:
                continue
                
            livros_base_count = base_counts.get(categoria, 0)
            livros_site_count = site_counts.get(categoria, 0)
            
            # CATEGORIA COMPLETAMENTE FALTANTE (0 na base, >0 no site)
            if livros_base_count == 0 and livros_site_count > 0:
                logger.info(f"🚨 CATEGORIA COMPLETAMENTE FALTANTE: {categoria}")
                self.discrepancies.append({
                    'tipo': 'CATEGORIA_FALTANTE',
                    'categoria': categoria,
                    'detalhes': f'CATEGORIA INTEIRA FALTANDO: Base tem 0 livros, site tem {livros_site_count}',
                    'severidade': 'CRITICA',
                    'livros_base': 0,
                    'livros_site': livros_site_count,
                    'faltantes': livros_site_count
                })
            
            # LIVROS FALTANTES EM CATEGORIA EXISTENTE
            elif livros_site_count > livros_base_count:
                faltantes = livros_site_count - livros_base_count
                
                # Verifica se são edições diferentes
                livros_site = livros_detalhados_site.get(categoria, [])
                edicoes_diferentes = self._encontrar_edicoes_diferentes(livros_site)
                
                if edicoes_diferentes:
                    logger.info(f"📚 {categoria}: {len(edicoes_diferentes)} títulos com edições diferentes")
                    for titulo, edicoes in edicoes_diferentes.items():
                        logger.info(f"   • '{titulo}': {len(edicoes)} edições (preços: {[ed['price'] for ed in edicoes]})")
                
                self.discrepancies.append({
                    'tipo': 'LIVROS_FALTANTES',
                    'categoria': categoria,
                    'detalhes': f'Base tem {livros_base_count} livros, site tem {livros_site_count} (faltam {faltantes})',
                    'severidade': 'ALTA',
                    'livros_base': livros_base_count,
                    'livros_site': livros_site_count,
                    'faltantes': faltantes,
                    'edicoes_diferentes': len(edicoes_diferentes) if edicoes_diferentes else 0
                })
                
            elif livros_base_count > livros_site_count:
                self.discrepancies.append({
                    'tipo': 'LIVROS_EXCEDENTES',
                    'categoria': categoria,
                    'detalhes': f'Base tem {livros_base_count} livros, site tem {livros_site_count} ({livros_base_count - livros_site_count} a mais)',
                    'severidade': 'BAIXA',
                    'livros_base': livros_base_count,
                    'livros_site': livros_site_count
                })

    def executar_recuperacao(self, max_categorias=10, max_tempo_minutos=30):
        """Recuperação COMPLETA - inclui categorias totalmente faltantes"""
        logger.info("🔄 Iniciando recuperação de dados COMPLETA")

        start_time = datetime.now()
        categorias_processadas = 0

        # CORREÇÃO: Inclui CATEGORIA_FALTANTE na recuperação
        categorias_para_recuperar = [
            disc for disc in self.discrepancies 
            if disc['severidade'] in ['CRITICA', 'ALTA', 'MEDIA'] 
            and disc['tipo'] in ['CATEGORIA_FALTANTE', 'LIVROS_FALTANTES']
        ]

        # Ordena por severidade (CRITICA primeiro)
        categorias_para_recuperar.sort(key=lambda x: {
            'CRITICA': 0, 'ALTA': 1, 'MEDIA': 2, 'BAIXA': 3
        }[x['severidade']])

        logger.info(f"📋 {len(categorias_para_recuperar)} categorias para recuperar")
        
        # Log das categorias que serão processadas
        for disc in categorias_para_recuperar:
            tipo_info = "CATEGORIA INTEIRA" if disc['tipo'] == 'CATEGORIA_FALTANTE' else f"{disc['faltantes']} livros"
            logger.info(f"   🎯 {disc['categoria']}: {tipo_info} ({disc['severidade']})")

        for discrepancia in categorias_para_recuperar:
            if (datetime.now() - start_time).total_seconds() > max_tempo_minutos * 60:
                logger.warning("⏰ Tempo máximo de execução atingido")
                break

            if categorias_processadas >= max_categorias:
                logger.info("🎯 Limite de categorias processadas atingido")
                break

            categoria = discrepancia['categoria']
            livros_faltantes = discrepancia.get('faltantes', 0)
            tipo = discrepancia['tipo']

            if tipo == 'CATEGORIA_FALTANTE':
                logger.info(f"🚨 RECUPERANDO CATEGORIA INTEIRA: {categoria} ({livros_faltantes} livros)")
            else:
                logger.info(f"📥 Recuperando {categoria} ({livros_faltantes} livros faltantes)")

            try:
                categoria_url = self._encontrar_url_categoria(categoria)
                if not categoria_url:
                    logger.error(f"❌ URL não encontrada para categoria: {categoria}")
                    continue
                
                # Scraping detalhado
                books_data = self._scrape_categoria_com_urls(categoria, categoria_url)

                novos_livros = 0
                edicoes_capturadas = 0

                for book_data in books_data:
                    if self._livro_nao_existe(book_data):
                        # Busca descrição completa apenas para livros novos
                        try:
                            book_data['description'] = self.scraper.get_book_description(book_data['_internal_url'])
                        except:
                            book_data['description'] = "Descrição não disponível"

                        # Remove campos internos antes de salvar
                        campos_internos = ['_internal_url', '_internal_url_id', '_internal_chave_unica']
                        for campo in campos_internos:
                            book_data.pop(campo, None)

                        self._salvar_livro(book_data)
                        novos_livros += 1

                        # Verifica se é uma edição diferente
                        livros_mesmo_titulo = self._contar_livros_mesmo_titulo(book_data['title'], categoria)
                        if livros_mesmo_titulo > 1:
                            edicoes_capturadas += 1
                            logger.info(f"   📚 Edição capturada: '{book_data['title']}' (£{book_data['price']})")

                if tipo == 'CATEGORIA_FALTANTE':
                    logger.info(f"🎉 CATEGORIA RECUPERADA: {categoria} - {novos_livros} livros salvos")
                else:
                    logger.info(f"✅ {categoria}: {novos_livros} novos livros ({edicoes_capturadas} edições)")
                    
                categorias_processadas += 1

            except Exception as e:
                logger.error(f"❌ Erro ao recuperar {categoria}: {e}")
                continue
            
        logger.info(f"🎉 Recuperação concluída: {categorias_processadas} categorias processadas")

    def _contar_livros_mesmo_titulo(self, titulo, categoria):
        """Conta quantos livros com mesmo título existem na categoria"""
        from app.models.book import Book
        return Book.query.filter_by(title=titulo, category=categoria).count()

    def _encontrar_url_categoria(self, categoria_nome):
        categorias_site = self.scraper.get_categories()
        for nome, url in categorias_site.items():
            if nome.strip().lower() == categoria_nome.strip().lower():
                return url
        return None
    
    def _livro_nao_existe(self, book_data):
        """Verificação usando apenas campos válidos do modelo Book"""
        from app.models.book import Book

        try:
            # Verificação por título e categoria (campos válidos)
            livro_existente = Book.query.filter_by(
                title=book_data['title'],
                category=book_data['category']
            ).first()

            # Se não existe, pode salvar
            if not livro_existente:
                return True

            # Se existe, verifica se é uma edição diferente (mesmo título, preço/rating diferente)
            if (livro_existente.price != book_data['price'] or 
                livro_existente.rating != book_data['rating']):
                logger.info(f"📚 Edição diferente encontrada: '{book_data['title']}'")
                logger.info(f"   Base: £{livro_existente.price} ⭐{livro_existente.rating}")
                logger.info(f"   Site: £{book_data['price']} ⭐{book_data['rating']}")
                return True

            return False
        
        except Exception as e:
            logger.error(f"Erro ao verificar livro existente: {e}")
            return True

    def _salvar_livro(self, book_data):
        from app.models.book import Book, db

        try:
            campos_validos = {
                'title': book_data['title'],
                'price': book_data['price'],
                'rating': book_data['rating'],
                'availability': book_data['availability'],
                'category': book_data['category'],
                'image_url': book_data.get('image_url', ''),
                'description': book_data.get('description', 'Descrição não disponível')
            }

            # Remover campos None ou vazios
            campos_validos = {k: v for k, v in campos_validos.items() if v is not None and v != ''}

            novo_livro = Book(**campos_validos)

            db.session.add(novo_livro)
            db.session.commit()
            logger.info(f"✅ Livro salvo: {book_data['title']}")

        except Exception as e:
            logger.error(f"❌ Erro ao salvar livro {book_data['title']}: {e}")
            db.session.rollback()

    def gerar_relatorio(self):
        """Gera relatório completo das discrepâncias"""
        if not self.discrepancies:
            return "CONCILIACAO: Sem discrepâncias encontradas"
        
        relatorio = ["RELATORIO DE CONCILIACAO", "="*50]
        
        por_tipo = defaultdict(list)
        for disc in self.discrepancies:
            por_tipo[disc['tipo']].append(disc)
        
        for tipo, disc_list in por_tipo.items():
            relatorio.append(f"\n{tipo} ({len(disc_list)} casos):")
            for disc in disc_list:
                if tipo == 'CATEGORIA_FALTANTE':
                    relatorio.append(f"   🚨 {disc['categoria']}: {disc['detalhes']}")
                else:
                    edicoes_info = f" - {disc.get('edicoes_diferentes', 0)} edições diferentes" if disc.get('edicoes_diferentes', 0) > 0 else ""
                    relatorio.append(f"   📚 {disc['categoria']}: {disc['detalhes']}{edicoes_info}")
        
        # Estatísticas resumidas
        total_faltantes = sum(disc.get('faltantes', 0) for disc in self.discrepancies)
        total_edicoes = sum(disc.get('edicoes_diferentes', 0) for disc in self.discrepancies)
        categorias_com_faltantes = len([disc for disc in self.discrepancies if disc.get('faltantes', 0) > 0])
        categorias_inteiras_faltantes = len([disc for disc in self.discrepancies if disc['tipo'] == 'CATEGORIA_FALTANTE'])
        
        relatorio.append(f"\n📊 RESUMO:")
        relatorio.append(f"   • {total_faltantes} livros faltantes no total")
        relatorio.append(f"   • {categorias_com_faltantes} categorias com livros faltantes")
        relatorio.append(f"   • {categorias_inteiras_faltantes} categorias INTEIRAS faltando")
        
        if total_edicoes > 0:
            relatorio.append(f"📚 EDIÇÕES DIFERENTES: {total_edicoes} títulos com múltiplas versões")
        
        return "\n".join(relatorio)

def main():
    from app.services.scraper import BookScraper
    from app import create_app, db
    
    app = create_app()
    
    with app.app_context():
        scraper = BookScraper()
        reconciliador = ScrapingReconciliation(scraper, db.session)
        
        discrepancies = reconciliador.analisar_conciliação()
        
        print(reconciliador.gerar_relatorio())
        
        if discrepancies:
            resposta = input("\nExecutar recuperacao automatica? (s/n): ")
            if resposta.lower() == 's':
                reconciliador.executar_recuperacao()
        
        print("Conciliação concluída")

if __name__ == "__main__":
    main()