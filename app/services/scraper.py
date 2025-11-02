import requests
from bs4 import BeautifulSoup
import time
import logging
from urllib.parse import urljoin

class BookScraper:
    def __init__(self, headless=True):
        """
        Inicializa o scraper com configurações básicas
        """
        self.base_url = "http://books.toscrape.com/"
        self.session = requests.Session()
        
        # HEADERS necessário para evitar bloqueio
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # LOGGER para debug e monitoramento
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        self.books_data = []
        self.logger.info(" >>> BookScraper inicializado com sucesso")

    def get_book_description(self, url):
        """
        Obtém a descrição do livro (limitada a 500 caracteres)
        """
        try:
            # USA self.headers que agora existe
            response = self.session.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Estratégia principal - seletor CSS que funciona
            description = soup.select_one('#product_description + p')
            if description:
                text = description.get_text(strip=True)
                if text and text != "":
                    # Limita a 500 caracteres como solicitado
                    return text[:500] + "..." if len(text) > 500 else text
            
            # Estratégia fallback - procurar por parágrafos longos
            all_paragraphs = soup.find_all('p')
            for p in all_paragraphs:
                text = p.get_text(strip=True)
                if text and len(text) > 50:
                    return text[:500] + "..." if len(text) > 500 else text
            
            return "Descrição não disponível"
            
        except Exception as e:
            # USA self.logger que agora existe
            self.logger.error(f"Erro ao obter descrição de {url}: {e}")
            return "Descrição não disponível"

    def get_categories(self):
        """Obtém todas as categorias de livros"""
        try:
            response = self.session.get(self.base_url, headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            categories = {}
            sidebar = soup.select('.side_categories ul li ul li a')
            
            for category in sidebar:
                category_name = category.get_text(strip=True)
                category_url = urljoin(self.base_url, category['href'])
                categories[category_name] = category_url
                
            self.logger.info(f"Encontradas {len(categories)} categorias")
            return categories
            
        except Exception as e:
            self.logger.error(f"Erro ao obter categorias: {e}")
            return {}

    def scrape_category(self, category_name, category_url):
        """Faz scraping de todos os livros de uma categoria"""
        try:
            self.logger.info(f"Scraping categoria: {category_name}")
            page_url = category_url
            
            while page_url:
                self.logger.info(f"Scraping página: {page_url}")
                response = self.session.get(page_url, headers=self.headers)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Encontra todos os livros na página
                books = soup.select('article.product_pod')
                
                for book in books:
                    book_data = self.scrape_book_details(book, category_name)
                    if book_data:
                        self.books_data.append(book_data)
                
                # Verifica se há próxima página
                next_button = soup.select_one('li.next a')
                if next_button:
                    page_url = urljoin(page_url, next_button['href'])
                else:
                    page_url = None
                
                time.sleep(1)  # Rate limiting
                    
        except Exception as e:
            self.logger.error(f"Erro ao fazer scraping da categoria {category_name}: {e}")

    def scrape_book_details(self, book_element, category_name):
        """Extrai detalhes de um livro individual com URL corrigida"""
        try:
            # URL do livro
            book_link = book_element.select_one('h3 a')
            if not book_link:
                return None

            # CORREÇÃO CRÍTICA: Lidar corretamente com URLs relativas
            book_relative_url = book_link['href']

            # Remove TODOS os ../ do início da URL
            while book_relative_url.startswith('../'):
                book_relative_url = book_relative_url[3:]

            # Garante que comece com catalogue/
            if not book_relative_url.startswith('catalogue/'):
                book_relative_url = f'catalogue/{book_relative_url}'

            book_url = urljoin(self.base_url, book_relative_url)

            # Informações básicas
            title = book_link.get('title', '').strip()

            # Preço - converte para float
            price_element = book_element.select_one('.price_color')
            price_text = price_element.get_text(strip=True) if price_element else "£0.00"
            # Remove £ e converte para float
            try:
                price = float(price_text.replace('£', ''))
            except:
                price = 0.0

            # Disponibilidade
            availability = book_element.select_one('.instock.availability')
            availability = availability.get_text(strip=True) if availability else "Out of stock"

            # Rating - converte texto para número
            rating_element = book_element.select_one('p.star-rating')
            rating = 0  # Default
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
                # Corrige URL da imagem
                while image_relative_url.startswith('../'):
                    image_relative_url = image_relative_url[3:]
                if not image_relative_url.startswith('catalogue/'):
                    image_relative_url = f'catalogue/{image_relative_url}'
                image_url = urljoin(self.base_url, image_relative_url)

            # Pega a descrição
            description = self.get_book_description(book_url)

            return {
                'title': title,
                'price': price,  # Já é float
                'availability': availability,
                'rating': rating,  # Já é integer
                'description': description,
                'category': category_name,
                'image_url': image_url,  # Nova campo
                'url': book_url
            }

        except Exception as e:
            self.logger.error(f"Erro ao extrair detalhes do livro: {e}")
            return None
        
    def get_all_books(self, max_categories=None):
        """
        Faz scraping de todos os livros de todas as categorias
        max_categories: limite para teste (None = todas)
        """
        self.books_data = []  # Reset dos dados
        
        categories = self.get_categories()
        
        # Limita para teste se especificado
        if max_categories:
            categories = dict(list(categories.items())[:max_categories])
            self.logger.info(f"🧪 Modo teste: processando {max_categories} categorias")
        
        total_categories = len(categories)
        
        for i, (category_name, category_url) in enumerate(categories.items(), 1):
            self.logger.info(f"📦 Processando categoria {i}/{total_categories}: {category_name}")
            self.scrape_category(category_name, category_url)
            time.sleep(2)  # Rate limiting entre categorias
            
        # Estatísticas finais
        total_books = len(self.books_data)
        with_desc = len([b for b in self.books_data if "Descrição não disponível" not in b['description']])
        success_rate = (with_desc / total_books) * 100 if total_books else 0
        
        self.logger.info(f"🎊 SCRAPING COMPLETO!")
        self.logger.info(f"📊 Total de livros: {total_books}")
        self.logger.info(f"📈 Taxa de sucesso: {success_rate:.1f}%")
            
        return self.books_data