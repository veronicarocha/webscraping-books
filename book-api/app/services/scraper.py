import requests
from bs4 import BeautifulSoup
import time
import logging
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class BookScraper:
    BASE_URL = "https://books.toscrape.com/"
    
    def __init__(self):
        self.session = requests.Session()
        self.books_data = []
    
    def scrape_all_books(self):
        """Extrai todos os livros do site"""
        categories = self.get_categories()
        
        for category_name, category_url in categories.items():
            logger.info(f"Scraping category: {category_name}")
            self.scrape_category(category_name, category_url)
            time.sleep(1)  # pausa pra não sobrecarregar o site
        
        return self.books_data
    
    def get_categories(self):
        """Obtém todas as categorias disponíveis"""
        categories = {}
        try:
            response = self.session.get(self.BASE_URL)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            category_list = soup.find('ul', class_='nav-list').find('ul').find_all('li')
            
            for category in category_list:
                link = category.find('a')
                category_name = link.text.strip()
                category_url = urljoin(self.BASE_URL, link['href'])
                categories[category_name] = category_url
                
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
        
        return categories
    
    def scrape_category(self, category_name, category_url):
        """Extrai livros de uma categoria específica"""
        page_url = category_url
        
        while page_url:
            try:
                response = self.session.get(page_url)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extrai livros da página atual
                books = soup.find_all('article', class_='product_pod')
                
                for book in books:
                    book_data = self.extract_book_data(book, category_name)
                    if book_data:
                        self.books_data.append(book_data)
                
                # Verifica se há próxima página
                next_button = soup.find('li', class_='next')
                if next_button:
                    next_link = next_button.find('a')['href']
                    page_url = urljoin(page_url, next_link)
                else:
                    page_url = None
                    
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error scraping category {category_name}: {e}")
                break
    
    def extract_book_data(self, book_element, category_name):
        """Extrai dados de um livro individual"""
        try:
            # Título
            title = book_element.find('h3').find('a')['title']
            
            # Preço
            price_text = book_element.find('p', class_='price_color').text
            price = float(price_text.replace('£', ''))
            
            # Rating
            rating_class = book_element.find('p', class_='star-rating')['class'][1]
            rating_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
            rating = rating_map.get(rating_class, 0)
            
            # Disponibilidade
            availability = book_element.find('p', class_='instock availability').text.strip()
            
            # URL da imagem
            image_url = book_element.find('img')['src']
            image_url = urljoin(self.BASE_URL, image_url)
            
            # URL do livro para pegar descrição
            book_url = book_element.find('h3').find('a')['href']
            book_url = urljoin(self.BASE_URL, book_url)
            
            # Pega descrição - ToDo - Ver
            description = self.get_book_description(book_url)
            
            return {
                'title': title,
                'price': price,
                'rating': rating,
                'availability': availability,
                'category': category_name,
                'image_url': image_url,
                'description': description
            }
            
        except Exception as e:
            logger.error(f"Error extracting book data: {e}")
            return None
    
    def get_book_description(self, book_url):
        try:
            response = self.session.get(book_url)
            soup = BeautifulSoup(response.content, 'html.parser')

            # v1: Descrição após div product_description
            product_desc_div = soup.find('div', id='product_description')
            if product_desc_div:
                next_p = product_desc_div.find_next_sibling('p')
                if next_p and next_p.text.strip():
                    description = next_p.text.strip()
                    # Limitando a 500 caracteres
                    if len(description) > 500:
                        return description[:500] + "..."
                    return description

            # v2: tentando pelo meta tag description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                desc = meta_desc['content'].strip()
                if desc and desc not in ["", "No description available", "Books to Scrape"]:
                    if len(desc) > 500:
                        return desc[:500] + "..."
                    return desc

            return "Descrição não disponível no momento."

        except Exception as e:
            logger.error(f"Error getting book description from {book_url}: {e}")
            return "Descrição não disponível no momento."