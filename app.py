from dotenv import load_dotenv
import os

from streamlit import text

# Carrega variáveis de ambiente
if os.path.exists('.env.local'):
    load_dotenv('.env.local')
    print(" >>> Configurações locais carregadas (.env.local)")
else:
    load_dotenv()
    print(" >>> Configurações padrão carregadas (.env)")

from app import create_app, db
from config import Config

app = create_app()

with app.app_context():
    try:
        # Testa a conexão com o banco
        db.session.execute(text('SELECT 1'))
        print(" Conexão com o banco estabelecida com sucesso")
    except Exception as e:
        print(f" Erro na conexão com o banco: {e}")
        print(f" URL do banco: {Config.SQLALCHEMY_DATABASE_URI}")
    
    db.create_all()
    print(" >>> Tabelas verificadas/criadas")

if __name__ == '__main__':
    print(f">>> Iniciando Book API em modo: {Config.check_environment()}")
    port = int(os.environ.get('PORT', 5000))
    debug = "local" in Config.check_environment().lower()
    app.run(host='0.0.0.0', port=port, debug=debug)