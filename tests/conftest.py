import pytest
from app import create_app, db
from app.models import User, Post
from werkzeug.security import generate_password_hash


@pytest.fixture
def app():
    """Create and configure a test app instance."""
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Create a test user."""
    user = User(
        username='testuser',
        password_hash=generate_password_hash('password123'),
        role='author'
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def test_post(app, test_user):
    """Create a test post."""
    post = Post(
        title='Test Post',
        slug='test-post',
        content='This is test content with [quiz id=1] shortcode.',
        status='published',
        author=test_user,
        categories=['Technology'],
        tags=['python', 'flask']
    )
    db.session.add(post)
    db.session.commit()
    return post


@pytest.fixture
def auth_client(client, test_user):
    """A test client that is logged in."""
    # Simulate login by setting session data
    with client:
        # This is a simplified login simulation
        # In a real test, you'd make a POST request to /login
        with client.session_transaction() as sess:
            sess['_user_id'] = str(test_user.id)
        yield client


@pytest.fixture
def admin_user(app):
    """Create an admin test user."""
    user = User(
        username='admin',
        password_hash=generate_password_hash('admin123'),
        role='admin'
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def admin_client(client, admin_user):
    """A test client logged in as admin."""
    with client:
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin_user.id)
        yield client
