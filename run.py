from dotenv import load_dotenv
load_dotenv()

import os
from app import create_app, db
from config import Config

app = create_app()

with app.app_context():
    db.create_all()
    print(">>>  Tabelas criadas - SCRAPER VIA COMANDO CLI")

if __name__ == '__main__':
    print(f">>> Iniciando Book API em modo: {Config.check_environment()}")
    port = int(os.environ.get('PORT', 5000))
    debug = Config.check_environment() == "desenvolvimento"
    app.run(host='0.0.0.0', port=port, debug=debug)