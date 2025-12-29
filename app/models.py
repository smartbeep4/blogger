from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
import re
from slugify import slugify


class User(UserMixin, db.Model):
    """User model for authentication and authorization."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='author')  # 'admin' or 'author'
    failed_attempts = db.Column(db.Integer, default=0)
    last_attempt = db.Column(db.DateTime)

    # Relationships
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify the user's password."""
        return check_password_hash(self.password_hash, password)

    def is_blocked(self):
        """Check if user account is blocked due to failed login attempts."""
        return self.failed_attempts >= 5

    def __repr__(self):
        return f'<User {self.username}>'


class Post(db.Model):
    """Post model for blog content."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)  # With shortcodes
    status = db.Column(db.String(20), nullable=False, default='draft')  # 'draft' or 'published'
    categories = db.Column(db.JSON, default=list)  # AI-generated categories
    tags = db.Column(db.JSON, default=list)  # AI-generated tags
    views = db.Column(db.Integer, default=0)
    published_at = db.Column(db.DateTime)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    revisions = db.relationship('Revision', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    quizzes = db.relationship('Quiz', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    charts = db.relationship('Chart', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    videos = db.relationship('Video', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    analytics_logs = db.relationship('AnalyticsLog', backref='post', lazy='dynamic', cascade='all, delete-orphan')

    def generate_slug(self):
        """Generate a URL-friendly slug from the title."""
        if not self.slug:
            base_slug = slugify(self.title)
            counter = 1
            slug = base_slug
            while Post.query.filter_by(slug=slug).first():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

    def increment_views(self):
        """Increment the view count."""
        self.views += 1
        db.session.commit()

    def __repr__(self):
        return f'<Post {self.title}>'


class Revision(db.Model):
    """Revision model for post version history."""
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Revision post_id={self.post_id} at {self.timestamp}>'


class Quiz(db.Model):
    """Quiz model for interactive quizzes."""
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    questions = db.Column(db.JSON, nullable=False)  # Array of question objects
    attempts = db.Column(db.Integer, default=0)
    successes = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Quiz id={self.id} post_id={self.post_id}>'


class Chart(db.Model):
    """Chart model for data visualizations."""
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    chart_type = db.Column(db.String(50), nullable=False)  # 'bar', 'line', 'pie', etc.
    data = db.Column(db.JSON, nullable=False)  # Chart.js configuration

    def __repr__(self):
        return f'<Chart id={self.id} post_id={self.post_id} type={self.chart_type}>'


class Video(db.Model):
    """Video model for embedded videos."""
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    filename = db.Column(db.String(200))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Video id={self.id} post_id={self.post_id}>'


class AnalyticsLog(db.Model):
    """Analytics log for tracking user interactions."""
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # 'view', 'quiz_attempt', 'quiz_success'
    ip_address = db.Column(db.String(45), nullable=False)  # IPv4/IPv6
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<AnalyticsLog post_id={self.post_id} event={self.event_type}>'


class BlockedIP(db.Model):
    """Blocked IP addresses due to failed login attempts."""
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), unique=True, nullable=False)  # IPv4/IPv6
    blocked_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    reason = db.Column(db.String(200), default='Failed login attempts')

    def __repr__(self):
        return f'<BlockedIP {self.ip_address}>'


@login.user_loader
def load_user(id):
    """Flask-Login user loader function."""
    return User.query.get(int(id))
