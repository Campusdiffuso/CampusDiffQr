from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from campusdiffuso.config import Config


db = SQLAlchemy()
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    mail.init_app(app)

    from campusdiffuso.users.routes import users
    from campusdiffuso.errors.handlers import errors
    app.register_blueprint(users)
    app.register_blueprint(errors)

    return app