import os
from src import create_app



if __name__ == "__main__":
    app = create_app()  
    app.run(host=app.config['IP_HOST'], port=app.config['PORT_HOST'], debug=app.config['DEBUG'])
