import pytest
from datetime import datetime
from app.models import User, Post, Revision, Quiz, Chart, Video, AnalyticsLog, BlockedIP, db


class TestUserModel:
    """Test User model functionality."""

    def test_password_hashing(self):
        """Test password hashing and verification."""
        user = User(username='testuser')
        user.set_password('password123')
        assert user.password_hash is not None
        assert user.check_password('password123')
        assert not user.check_password('wrongpassword')

    def test_user_creation(self):
        """Test user creation with required fields."""
        user = User(username='testuser', role='author')
        assert user.username == 'testuser'
        assert user.role == 'author'
        assert user.failed_attempts == 0

    def test_is_blocked(self):
        """Test user blocking logic."""
        user = User()
        assert not user.is_blocked()

        user.failed_attempts = 5
        assert user.is_blocked()


class TestPostModel:
    """Test Post model functionality."""

    def test_post_creation(self):
        """Test post creation with required fields."""
        user = User(id=1, username='author')
        post = Post(
            title='Test Post',
            content='Test content',
            author=user
        )
        assert post.title == 'Test Post'
        assert post.content == 'Test content'
        assert post.status == 'draft'
        assert post.views == 0

    def test_slug_generation(self):
        """Test automatic slug generation."""
        post = Post(title='Test Post Title')
        post.generate_slug()
        assert post.slug == 'test-post-title'

        # Test duplicate handling
        post2 = Post(title='Test Post Title')
        post2.generate_slug()
        assert post2.slug == 'test-post-title-1'

    def test_increment_views(self):
        """Test view increment functionality."""
        post = Post()
        initial_views = post.views
        post.increment_views()
        assert post.views == initial_views + 1


class TestRevisionModel:
    """Test Revision model functionality."""

    def test_revision_creation(self):
        """Test revision creation."""
        revision = Revision(
            post_id=1,
            content='Revision content',
            timestamp=datetime.utcnow()
        )
        assert revision.post_id == 1
        assert revision.content == 'Revision content'


class TestQuizModel:
    """Test Quiz model functionality."""

    def test_quiz_creation(self):
        """Test quiz creation."""
        quiz = Quiz(
            post_id=1,
            questions=[{'question': 'Test?', 'type': 'multiple_choice', 'answer': 'A'}]
        )
        assert quiz.post_id == 1
        assert len(quiz.questions) == 1
        assert quiz.attempts == 0
        assert quiz.successes == 0


class TestChartModel:
    """Test Chart model functionality."""

    def test_chart_creation(self):
        """Test chart creation."""
        chart = Chart(
            post_id=1,
            chart_type='bar',
            data={'labels': ['A', 'B'], 'datasets': [{'data': [1, 2]}]}
        )
        assert chart.post_id == 1
        assert chart.chart_type == 'bar'
        assert 'labels' in chart.data


class TestVideoModel:
    """Test Video model functionality."""

    def test_video_creation(self):
        """Test video creation."""
        video = Video(
            post_id=1,
            url='https://example.com/video.mp4',
            filename='video.mp4'
        )
        assert video.post_id == 1
        assert video.url == 'https://example.com/video.mp4'
        assert video.filename == 'video.mp4'


class TestAnalyticsLogModel:
    """Test AnalyticsLog model functionality."""

    def test_analytics_log_creation(self):
        """Test analytics log creation."""
        log = AnalyticsLog(
            post_id=1,
            event_type='view',
            ip_address='127.0.0.1'
        )
        assert log.post_id == 1
        assert log.event_type == 'view'
        assert log.ip_address == '127.0.0.1'


class TestBlockedIPModel:
    """Test BlockedIP model functionality."""

    def test_blocked_ip_creation(self):
        """Test blocked IP creation."""
        blocked = BlockedIP(
            ip_address='192.168.1.1',
            reason='Failed login attempts'
        )
        assert blocked.ip_address == '192.168.1.1'
        assert blocked.reason == 'Failed login attempts'


class TestModelRelationships:
    """Test model relationships."""

    def test_user_posts_relationship(self):
        """Test user-posts relationship."""
        user = User(username='author', role='author')
        post = Post(title='Test', content='Content', author=user)

        assert post.author == user
        assert post in user.posts

    def test_post_revisions_relationship(self):
        """Test post-revisions relationship."""
        post = Post(title='Test', content='Content')
        revision = Revision(post=post, content='Revised content')

        assert revision.post == post
        assert revision in post.revisions
