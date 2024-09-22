"""Main application routes."""

from flask_restx import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import cache
from . import main_ns


@main_ns.route('/protected')
class Protected(Resource):
    """Protected Resource."""

    decorators = [jwt_required(), cache.cached(timeout=50)]

    @main_ns.response(200, 'Success')
    @main_ns.response(401, 'Unauthorized')
    def get(self):
        """Protected route that requires authentication."""
        user_id = get_jwt_identity()
        return {"message": f"Hello, user {user_id}!"}, 200


@main_ns.route('/public')
class Public(Resource):
    """Public Resource."""

    @main_ns.response(200, 'Success')
    def get(self):
        """Public route accessible without authentication."""
        return {"message": "This is a public endpoint."}, 200