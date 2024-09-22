"""Initialize the authentication namespace."""

from flask_restx import Namespace

auth_ns = Namespace('auth', description='Authentication operations')

from . import routes  # noqa: F401, E402