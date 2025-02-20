import os
from dotenv import load_dotenv 
from src.app import create_app 

load_dotenv()

class Middleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        environ.update({"Id": 1})
        environ.update({"email": "hrpbs@teste.com"})
        return self.app(environ, start_response)

app = create_app()
app.wsgi_app = Middleware(app.wsgi_app)

if __name__ == "__main__":
    app.run(debug=True, port=app.config['PORT'], host="0.0.0.0")