from config import Config
from app import create_app
import logging


app = create_app(Config)
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
