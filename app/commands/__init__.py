#forçando deploy
def register_commands(app):
    from app.commands.scraper import scrape_books_command
    app.cli.add_command(scrape_books_command)