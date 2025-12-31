import os
import click
from app import create_app, db
from app.models import User, Post
from datetime import datetime

# Determine config based on environment
config_name = os.environ.get('FLASK_ENV', 'default')
if config_name == 'production':
    config_name = 'production'
elif config_name == 'development':
    config_name = 'development'
else:
    config_name = 'default'

# Create the Flask application
app = create_app(config_name)


@app.cli.command('create-admin')
@click.option('--username', default='admin', help='Admin username')
@click.option('--password', default='admin123', help='Admin password')
def create_admin(username, password):
    """Create an admin user."""
    with app.app_context():
        # Check if user already exists
        existing = User.query.filter_by(username=username).first()
        if existing:
            click.echo(f'User "{username}" already exists.')
            return
        
        admin = User(username=username, role='admin')
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        click.echo(f'Admin user created: {username}/{password}')


@app.cli.command('seed-posts')
def seed_posts():
    """Seed the database with sample blog posts."""
    with app.app_context():
        # Get or create admin user
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            click.echo('No admin user found. Run "flask create-admin" first.')
            return
        
        # Check if posts already exist
        if Post.query.count() > 0:
            click.echo('Posts already exist in the database.')
            return
        
        sample_posts = [
            {
                'title': 'Getting Started with Interactive Blogging',
                'slug': 'getting-started-interactive-blogging',
                'content': '''<h2>Welcome to the Future of Blogging</h2>
<p>This platform allows you to create rich, interactive content that engages your readers like never before. With built-in support for quizzes, charts, videos, and PDFs, you can transform your blog posts into immersive experiences.</p>

<h3>Key Features</h3>
<ul>
<li><strong>Rich Text Editor</strong> - Powered by Quill.js for a seamless writing experience</li>
<li><strong>Interactive Quizzes</strong> - Test your readers' knowledge with embedded quizzes</li>
<li><strong>Data Visualizations</strong> - Add charts and graphs to illustrate your points</li>
<li><strong>Media Embedding</strong> - Include videos and PDFs directly in your posts</li>
</ul>

<h3>Getting Started</h3>
<p>To create your first post, simply log in to the dashboard and click "New Post". The intuitive editor will guide you through the process of crafting compelling content.</p>

<p>We're excited to have you here. Happy blogging!</p>''',
                'status': 'published',
                'categories': ['Tutorial', 'Technology'],
                'tags': ['getting-started', 'blogging', 'tutorial', 'features'],
            },
            {
                'title': 'The Power of AI in Content Creation',
                'slug': 'power-of-ai-content-creation',
                'content': '''<h2>How AI is Revolutionizing Blogging</h2>
<p>Artificial Intelligence has transformed how we create and consume content. From automatic tag generation to content suggestions, AI tools are making bloggers more productive than ever.</p>

<h3>AI-Powered Features on This Platform</h3>
<p>This blog uses Google's Gemini AI to automatically generate relevant categories and tags for your posts. This means less time organizing and more time creating.</p>

<h3>The Future of Content</h3>
<p>As AI technology continues to evolve, we can expect even more innovative features that help content creators focus on what matters most - telling great stories and sharing valuable insights.</p>

<blockquote>The best content combines human creativity with AI-powered efficiency.</blockquote>

<p>What are your thoughts on AI in content creation? The conversation is just beginning.</p>''',
                'status': 'published',
                'categories': ['Technology', 'Opinion'],
                'tags': ['ai', 'content-creation', 'gemini', 'future', 'technology'],
            },
            {
                'title': 'Building Modern Web Applications with Flask',
                'slug': 'building-modern-web-applications-flask',
                'content': '''<h2>Why Flask is Perfect for Modern Web Apps</h2>
<p>Flask is a lightweight yet powerful Python web framework that gives you the flexibility to build applications your way. This very blog is built with Flask!</p>

<h3>Key Advantages</h3>
<ul>
<li><strong>Simplicity</strong> - Easy to learn and get started</li>
<li><strong>Flexibility</strong> - Choose your own tools and libraries</li>
<li><strong>Scalability</strong> - Grows with your application</li>
<li><strong>Community</strong> - Large ecosystem of extensions</li>
</ul>

<h3>Tech Stack Overview</h3>
<p>This blog uses:</p>
<ul>
<li>Flask 3.0 with SQLAlchemy ORM</li>
<li>PostgreSQL for data persistence</li>
<li>Tailwind CSS for beautiful styling</li>
<li>Alpine.js for lightweight interactivity</li>
</ul>

<p>Whether you're building a simple blog or a complex web application, Flask provides the foundation you need to succeed.</p>''',
                'status': 'published',
                'categories': ['Technology', 'Tutorial'],
                'tags': ['flask', 'python', 'web-development', 'programming', 'tutorial'],
            },
        ]
        
        for post_data in sample_posts:
            post = Post(
                title=post_data['title'],
                slug=post_data['slug'],
                content=post_data['content'],
                status=post_data['status'],
                categories=post_data['categories'],
                tags=post_data['tags'],
                author_id=admin.id,
                published_at=datetime.utcnow(),
                views=0
            )
            db.session.add(post)
        
        db.session.commit()
        click.echo(f'Created {len(sample_posts)} sample blog posts.')


if __name__ == '__main__':
    # Run the development server
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config.get('DEBUG', False)
    )
