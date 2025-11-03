from .scrape_command import scrape_books_command

def register_commands(app):
    """Registra comandos CLI personalizados"""
    app.cli.add_command(scrape_books_command)