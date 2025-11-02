def register_commands(app):
    from app.commands.scrape import scrape_books_command
    app.cli.add_command(scrape_books_command)