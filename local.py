from dotenv import load_dotenv
load_dotenv()

from src import create_app
app = create_app()


# host="0.0.0.0"

if __name__ == "__main__":
    app.run(debug=True, port=8600)