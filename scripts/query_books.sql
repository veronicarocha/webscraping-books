-- subir o dash
$ streamlit run app.py

-- ativar o vevn
$ source venv/Scripts/activate

-- conectar ao container PostgreSQL
docker exec -it postgres-books psql -U postgres -d booksapi

-- limpar o cache do flask 
python -c "import app; print('Cache limpo')"

--limpar os caches do python
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete

-- para o Railway
railway login
railway list
railway link
railway run python -c "from app import create_app, db; app = create_app(); with app.app_context(): db.create_all(); print('✅ Tabelas criadas!')"


-- conecta 
\c booksapi

-- sair 
\q

-- listar as bases
\l

-- Listar todas as tabelas
\dt

-- Ver estrutura da tabela books
\d+ books

-- Contar total de livros
SELECT COUNT(*) FROM books;

-- Ver algumas categorias
SELECT DISTINCT category FROM books LIMIT 10;

-- Ver livros mais caros
SELECT title, price, category FROM books ORDER BY price DESC LIMIT 5;

-- Ver distribuição por rating
SELECT rating, COUNT(*) FROM books GROUP BY rating ORDER BY rating;

-- Estatísticas gerais
SELECT 
    COUNT(*) as total_livros,
    COUNT(DISTINCT category) as total_categorias,
    ROUND(AVG(price), 2) as preco_medio,
    MAX(price) as preco_maximo,
    MIN(price) as preco_minimo
FROM books;

-- Top categorias com mais livros
SELECT 
    category,
    COUNT(*) as quantidade,
    ROUND(AVG(price), 2) as preco_medio
FROM books 
GROUP BY category 
ORDER BY quantidade DESC 
LIMIT 10;

-- Livros com rating 5
SELECT title, price, category 
FROM books 
WHERE rating = 5 
ORDER BY price DESC 
LIMIT 10;

-- Ver disponibilidade dos livros
SELECT availability, COUNT(*) 
FROM books 
GROUP BY availability;

-- Livros com descrição mais longa
SELECT title, LENGTH(description) as desc_length 
FROM books 
ORDER BY desc_length DESC 
LIMIT 5;

-- Preço médio por rating
SELECT rating, ROUND(AVG(price), 2) as avg_price
FROM books 
GROUP BY rating 
ORDER BY rating;