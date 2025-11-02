from dotenv import load_dotenv
load_dotenv()

import os
from app import create_app
from config import Config

app = create_app()

if __name__ == '__main__':
    print(f">>> Iniciando Book API em modo: {Config.check_environment()}")
    print(f">>> Database: {Config.SQLALCHEMY_DATABASE_URI}")
    
    port = int(os.environ.get('PORT', 5000))
    debug = Config.check_environment() == "desenvolvimento"
    
    app.run(host='0.0.0.0', port=port, debug=debug)