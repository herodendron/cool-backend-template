"""Initialize Flask extensions."""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_restx import Api
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
api = Api(
    title='Cool Backend Template',
    version='1.0',
    description='A professional (cool!) Flask API backend template',
    doc='/docs'
)
cache = Cache()
limiter = Limiter(key_func=get_remote_address)