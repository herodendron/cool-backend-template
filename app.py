"""Main application file for the Flask API."""

from flask import Flask
from config import Config
from extensions import db, jwt, migrate, api, cache, limiter
from auth import auth_ns
from main import main_ns
from flask_swagger_ui import get_swaggerui_blueprint


def create_app():
    """Create and configure the Flask application.

    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)
    api.init_app(app)

    # Register namespaces
    api.add_namespace(auth_ns, path='/auth')
    api.add_namespace(main_ns, path='/api')

    # Swagger UI setup
    SWAGGER_URL = '/swagger'
    API_URL = '/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={'app_name': "Flask API Backend"}
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    return app


if __name__ == "__main__":
    application = create_app()
    application.run()