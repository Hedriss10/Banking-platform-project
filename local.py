from src.external import create_app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=8000) # port 8000 for not problem