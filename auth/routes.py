"""Routes for user authentication."""

from flask import request
from flask_restx import Resource, fields
from models import User
from extensions import db, jwt
from flask_jwt_extended import create_access_token
from werkzeug.exceptions import BadRequest, Conflict, InternalServerError, Unauthorized
from marshmallow import Schema, fields as ma_fields, ValidationError
from extensions import limiter
from . import auth_ns

user_model = auth_ns.model('User', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password'),
})


class UserSchema(Schema):
    username = ma_fields.Str(required=True)
    password = ma_fields.Str(required=True)


user_schema = UserSchema()


@auth_ns.route('/register')
class Register(Resource):
    """User Registration Resource."""

    decorators = [limiter.limit("5 per minute")]

    @auth_ns.expect(user_model, validate=True)
    @auth_ns.response(201, 'User registered successfully.')
    @auth_ns.response(400, 'Invalid input.')
    @auth_ns.response(409, 'User already exists.')
    @auth_ns.response(500, 'Registration failed.')
    def post(self):
        """Register a new user."""
        try:
            data = user_schema.load(request.json)
        except ValidationError as err:
            raise BadRequest(err.messages)

        if User.query.filter_by(username=data["username"]).first():
            raise Conflict("User already exists.")

        new_user = User(username=data["username"])
        new_user.set_password(data["password"])
        db.session.add(new_user)
        try:
            db.session.commit()
            return {"message": "User registered successfully."}, 201
        except Exception:
            db.session.rollback()
            raise InternalServerError("Registration failed.")


@auth_ns.route('/login')
class Login(Resource):
    """User Login Resource."""

    decorators = [limiter.limit("10 per minute")]

    @auth_ns.expect(user_model, validate=True)
    @auth_ns.response(200, 'Access token issued.')
    @auth_ns.response(400, 'Invalid input.')
    @auth_ns.response(401, 'Invalid credentials.')
    def post(self):
        """Authenticate a user and return a JWT token."""
        try:
            data = user_schema.load(request.json)
        except ValidationError as err:
            raise BadRequest(err.messages)

        user = User.query.filter_by(username=data["username"]).first()
        if user and user.check_password(data["password"]):
            access_token = create_access_token(identity=user.id)
            return {"access_token": access_token}, 200
        else:
            raise Unauthorized("Invalid credentials.")