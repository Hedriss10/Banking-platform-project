import os
from src import create_app


os.environ['production']

if __name__ == "__main__":
    app = create_app()  
    app.run(host=app.config['IP_HOST'], port=app.config['PORT'], debug=app.config['DEGUG'])