"""Unit tests for main routes."""

import unittest
from app import create_app
from extensions import db
from models import User
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "test-secret-key"
    JWT_SECRET_KEY = "test-jwt-secret-key"
    RATELIMIT_ENABLED = False  # Disable rate limiting for tests


class MainTestCase(unittest.TestCase):
    """Test cases for main application."""

    def setUp(self):
        """Set up test variables."""
        self.app = create_app()
        self.app.config.from_object(TestConfig)
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            user = User(username='testuser')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            response = self.client.post('/auth/login', json={
                'username': 'testuser',
                'password': 'password123'
            })
            self.access_token = response.json['access_token']

    def tearDown(self):
        """Tear down test variables."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_public_route(self):
        """Test the public route."""
        response = self.client.get('/api/public')
        self.assertEqual(response.status_code, 200)
        self.assertIn('This is a public endpoint.', response.json['message'])

    def test_protected_route_without_token(self):
        """Test accessing protected route without a token."""
        response = self.client.get('/api/protected')
        self.assertEqual(response.status_code, 401)

    def test_protected_route_with_token(self):
        """Test accessing protected route with a valid token."""
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        response = self.client.get('/api/protected', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Hello, user', response.json['message'])


if __name__ == "__main__":
    unittest.main()