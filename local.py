from src.external import creat_app

if __name__ == "__main__":
    app = creat_app()
    app.run(debug=True, port=8000) # port 8000 for not problem
    
    