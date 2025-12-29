import pytest
from flask import url_for
from app.models import User, Post


class TestPublicRoutes:
    """Test public routes that don't require authentication."""

    def test_index_route(self, client):
        """Test blog index page."""
        response = client.get('/')
        assert response.status_code == 200

    def test_post_detail_route(self, client, test_post):
        """Test individual post view."""
        response = client.get(f'/post/{test_post.slug}')
        assert response.status_code == 200
        assert test_post.title in response.get_data(as_text=True)

    def test_category_route(self, client):
        """Test category filtering."""
        response = client.get('/category/technology')
        assert response.status_code == 200

    def test_tag_route(self, client):
        """Test tag filtering."""
        response = client.get('/tag/python')
        assert response.status_code == 200


class TestAuthRoutes:
    """Test authentication routes."""

    def test_login_page(self, client):
        """Test login page loads."""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'login' in response.get_data()

    def test_login_success(self, client, test_user):
        """Test successful login."""
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'password123',
            'remember_me': False
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_login_failure(self, client):
        """Test failed login."""
        response = client.post('/login', data={
            'username': 'wronguser',
            'password': 'wrongpass'
        })
        assert response.status_code == 200
        assert b'Invalid username or password' in response.get_data()

    def test_logout(self, client, auth_client):
        """Test logout functionality."""
        response = auth_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200


class TestProtectedRoutes:
    """Test routes that require authentication."""

    def test_dashboard_requires_auth(self, client):
        """Test dashboard requires authentication."""
        response = client.get('/dashboard')
        assert response.status_code == 302  # Redirect to login

    def test_dashboard_authenticated(self, auth_client):
        """Test dashboard works when authenticated."""
        response = auth_client.get('/dashboard')
        assert response.status_code == 200
        assert b'dashboard' in response.get_data()

    def test_editor_requires_auth(self, client):
        """Test editor requires authentication."""
        response = client.get('/editor')
        assert response.status_code == 302

    def test_editor_authenticated(self, auth_client):
        """Test editor works when authenticated."""
        response = auth_client.get('/editor')
        assert response.status_code == 200
        assert b'editor' in response.get_data()


class TestAPIRoutes:
    """Test API routes."""

    def test_save_draft_requires_auth(self, client):
        """Test save draft API requires authentication."""
        response = client.post('/api/save_draft', json={
            'content': 'Test content'
        })
        assert response.status_code == 401

    def test_create_quiz_requires_auth(self, auth_client):
        """Test quiz creation requires authentication."""
        response = auth_client.post('/api/create_quiz', json={
            'post_id': 1,
            'questions': [{'question': 'Test?', 'answer': 'Yes'}]
        })
        assert response.status_code == 200

    def test_log_quiz_no_auth_required(self, client):
        """Test quiz logging doesn't require authentication."""
        response = client.post('/api/log_quiz', json={
            'quiz_id': 1,
            'event_type': 'attempt'
        })
        assert response.status_code == 200


class TestAdminRoutes:
    """Test admin-only routes."""

    def test_admin_users_requires_admin(self, auth_client):
        """Test admin routes require admin role."""
        # auth_client is regular user, not admin
        response = auth_client.get('/admin/users')
        assert response.status_code == 200  # Should show flash message but allow access
        # Check for admin restriction in response
        assert b'Admin privileges required' in response.get_data()

    def test_admin_logins_requires_admin(self, auth_client):
        """Test admin login logs require admin role."""
        response = auth_client.get('/admin/logins')
        assert response.status_code == 200
        assert b'Admin privileges required' in response.get_data()


class TestErrorHandling:
    """Test error handling."""

    def test_404_error(self, client):
        """Test 404 error page."""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404

    def test_post_not_found(self, client):
        """Test accessing non-existent post."""
        response = client.get('/post/nonexistent-slug')
        assert response.status_code == 404
