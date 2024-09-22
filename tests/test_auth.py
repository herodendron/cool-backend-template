"""Unit tests for authentication routes."""

import unittest
from app import create_app
from extensions import db
from models import User
import json
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "test-secret-key"
    JWT_SECRET_KEY = "test-jwt-secret-key"
    RATELIMIT_ENABLED = False  # Disable rate limiting for tests


class AuthTestCase(unittest.TestCase):
    """Test cases for authentication."""

    def setUp(self):
        """Set up test variables."""
        self.app = create_app()
        self.app.config.from_object(TestConfig)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Tear down test variables."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register(self):
        """Test user registration."""
        response = self.client.post('/auth/register', json={
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 201)

    def test_login(self):
        """Test user login."""
        with self.app.app_context():
            user = User(username='testuser')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
        response = self.client.post('/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', json.loads(response.data))

    def test_invalid_login(self):
        """Test login with invalid credentials."""
        response = self.client.post('/auth/login', json={
            'username': 'nonexistent',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 401)

    def test_register_existing_user(self):
        """Test registering an existing user."""
        with self.app.app_context():
            user = User(username='testuser')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
        response = self.client.post('/auth/register', json={
            'username': 'testuser',
            'password': 'newpassword'
        })
        self.assertEqual(response.status_code, 409)


if __name__ == "__main__":
    unittest.main()