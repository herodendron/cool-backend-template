"""Database models for the Flask application."""

from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    """User model for storing user credentials."""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        """Hash and store the user's password.

        Args:
            password (str): The plaintext password.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the stored hash.

        Args:
            password (str): The plaintext password.

        Returns:
            bool: True if passwords match, False otherwise.
        """
        return check_password_hash(self.password_hash, password)