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
    # config_by_name[flask_env].DEBUG
    # gunicorn -w 4 -b 0.0.0.0:5002 'src.app:create_app()'
    app.run(port=5002, debug=True, host="0.0.0.0")
