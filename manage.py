from src import create_app

class Middleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        environ.update({"Id": 1047})
        environ.update({"email": "usersbs@teste.com"})
        return self.app(environ, start_response)

app = create_app()
app.wsgi_app = Middleware(app.wsgi_app)

if __name__ == "__main__":
    app.run(debug=True, port=app.config['PORT'], host="0.0.0.0")