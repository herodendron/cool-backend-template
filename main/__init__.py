"""Initialize the main namespace."""

from flask_restx import Namespace

main_ns = Namespace('main', description='Main application operations')

from . import routes  # noqa: F401, E402