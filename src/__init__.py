from dotenv import load_dotenv
from flask import Flask


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    # the path to your .env file (or any other file of environment variables you want to load)
    load_dotenv('.env')
    app.config.from_pyfile('../settings.py')

    if __name__ == '__main__':
        app.run(debug=True)

    return app
