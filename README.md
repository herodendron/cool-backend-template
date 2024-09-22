# Cool Backend Template

## Description

A professional, industry-standard Flask backend API template designed for flexibility, customization, and efficiency. This template provides a solid foundation for building robust APIs with Flask, incorporating best practices and modern development workflows.

## Features

- **Modular Code Structure**: Organized using Blueprints and Namespaces for scalability.
- **JWT Authentication and Authorization**: Secure login and protected routes using JSON Web Tokens.
- **Input Validation**: Ensures data integrity with Marshmallow schemas.
- **Rate Limiting**: Prevents abuse with Flask-Limiter.
- **Caching**: Improves performance with Flask-Caching.
- **Comprehensive Logging**: Integrated logging for monitoring and debugging.
- **Automated API Documentation**: Swagger UI integration for interactive API exploration.
- **Testing**: Unit and integration tests with high coverage using unittest.
- **Docker Support**: Containerization for easy deployment.
- **Asynchronous Tasks**: Ready for Celery integration (optional).

## Table of Contents

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Running Tests](#running-tests)
- [Deployment](#deployment)
  - [Using Docker](#using-docker)
- [Adding New Functionality](#adding-new-functionality)
  - [Example: Adding a New Endpoint](#example-adding-a-new-endpoint)
- [Contributing](#contributing)
- [License](#license)

## Getting Started

### Prerequisites

- **Python 3.8 or higher**
- **Virtual environment tool**: `venv`, `virtualenv`, or `conda`
- **Docker** (optional, for containerization)
- **Git** (to clone the repository)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/herodendron/cool-backend-template.git
   cd cool-backend-template
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```

   - On Unix or MacOS:

     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**

   - Copy `.env.example` to `.env`

     ```bash
     cp .env.example .env
     ```

   - Open `.env` and fill in your secret keys and database URL:

     ```ini
     SECRET_KEY=your-secret-key
     JWT_SECRET_KEY=your-jwt-secret-key
     DATABASE_URL=sqlite:///app.db
     ```

6. **Initialize the database**

   ```bash
   flask db upgrade
   ```

   - If the `flask` command is not recognized, you may need to set the `FLASK_APP` environment variable:

     ```bash
     export FLASK_APP=app.py
     ```

## Running the Application

Start the Flask development server:

```bash
flask run
```

The application will be available at `http://localhost:5000/`.

## API Documentation

After running the application, access the Swagger UI at `http://localhost:5000/swagger` to explore the API endpoints interactively.

## Running Tests

Execute the test suite using the following command:

```bash
python -m unittest discover tests
```

This will run all unit and integration tests located in the `tests` directory.

## Deployment

For production deployment, it's recommended to use Docker and a WSGI server like Gunicorn.

### Using Docker

1. **Build the Docker image**

   ```bash
   docker build -t cool-backend-template .
   ```

2. **Run the Docker container**

   ```bash
   docker run -d -p 5000:5000 --env-file .env cool-backend-template
   ```

   - Ensure that the `.env` file is properly configured with your production settings.

## Adding New Functionality

The template is designed to be easily extendable. Below is a step-by-step guide on how to add new functionality, such as a new endpoint with its corresponding database model.

### Example: Adding a New Endpoint

Suppose you want to add a new resource called `Item` with CRUD (Create, Read, Update, Delete) operations.

#### 1. Create the Database Model

In `models.py`, add the new `Item` model:

```python
# models.py

class Item(db.Model):
    """Item model for storing item details."""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f'<Item {self.name}>'
```

#### 2. Generate a Migration

Run the following commands to generate and apply the database migration:

```bash
flask db migrate -m "Add Item model"
flask db upgrade
```

#### 3. Create a New Namespace

Create a new directory `items` for the `Item` resource:

```bash
mkdir items
touch items/__init__.py
touch items/routes.py
```

In `items/__init__.py`, initialize the namespace:

```python
# items/__init__.py

from flask_restx import Namespace

items_ns = Namespace('items', description='Item operations')

from . import routes  # noqa: F401, E402
```

#### 4. Define the Routes

In `items/routes.py`, add the CRUD endpoints:

```python
# items/routes.py

from flask_restx import Resource, fields
from models import Item
from extensions import db
from . import items_ns

item_model = items_ns.model('Item', {
    'id': fields.Integer(readOnly=True, description='The unique identifier of an item'),
    'name': fields.String(required=True, description='Item name'),
    'description': fields.String(description='Item description'),
})

@items_ns.route('/')
class ItemList(Resource):
    @items_ns.marshal_list_with(item_model)
    def get(self):
        """List all items"""
        return Item.query.all()

    @items_ns.expect(item_model, validate=True)
    @items_ns.marshal_with(item_model, code=201)
    def post(self):
        """Create a new item"""
        data = items_ns.payload
        new_item = Item(name=data['name'], description=data.get('description'))
        db.session.add(new_item)
        db.session.commit()
        return new_item, 201

@items_ns.route('/<int:id>')
@items_ns.response(404, 'Item not found')
class ItemResource(Resource):
    @items_ns.marshal_with(item_model)
    def get(self, id):
        """Fetch an item given its identifier"""
        item = Item.query.get_or_404(id)
        return item

    @items_ns.expect(item_model, validate=True)
    @items_ns.marshal_with(item_model)
    def put(self, id):
        """Update an item given its identifier"""
        item = Item.query.get_or_404(id)
        data = items_ns.payload
        item.name = data['name']
        item.description = data.get('description')
        db.session.commit()
        return item

    @items_ns.response(204, 'Item deleted')
    def delete(self, id):
        """Delete an item given its identifier"""
        item = Item.query.get_or_404(id)
        db.session.delete(item)
        db.session.commit()
        return '', 204
```

#### 5. Register the Namespace

In `app.py`, import and add the new namespace to the API:

```python
# app.py

from items import items_ns  # Add this import

def create_app():
    # ...

    # Register namespaces
    api.add_namespace(auth_ns, path='/auth')
    api.add_namespace(main_ns, path='/api')
    api.add_namespace(items_ns, path='/api/items')  # Add this line

    # ...
```

#### 6. Update the API Documentation

The Swagger UI will automatically update to include the new `items` endpoints since we are using Flask-RESTX, which integrates with Swagger UI.

#### 7. Test the New Endpoints

Start the application and navigate to `http://localhost:5000/swagger` to see and test the new `items` endpoints.

#### 8. Add Unit Tests

Create a new test file `tests/test_items.py`:

```python
# tests/test_items.py

import unittest
from app import create_app
from extensions import db
from models import Item
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "test-secret-key"
    JWT_SECRET_KEY = "test-jwt-secret-key"
    RATELIMIT_ENABLED = False  # Disable rate limiting for tests

class ItemsTestCase(unittest.TestCase):
    """Test cases for Item resource."""

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

    def test_create_item(self):
        """Test creating a new item."""
        response = self.client.post('/api/items/', json={
            'name': 'Test Item',
            'description': 'This is a test item.'
        })
        self.assertEqual(response.status_code, 201)

    def test_get_items(self):
        """Test retrieving items."""
        # First, create an item
        self.client.post('/api/items/', json={
            'name': 'Test Item',
            'description': 'This is a test item.'
        })
        # Then, retrieve items
        response = self.client.get('/api/items/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json) > 0)

if __name__ == "__main__":
    unittest.main()
```

Run the tests:

```bash
python -m unittest tests/test_items.py
```

#### 9. Commit Your Changes

Add and commit your changes to version control:

```bash
git add .
git commit -m "Add Item resource with CRUD endpoints"
```

