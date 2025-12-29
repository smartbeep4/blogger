# Interactive Blog Platform

A modern, interactive blog platform built with Flask featuring rich text editing, embedded quizzes, charts, videos, and PDF viewers. Includes AI-powered tag generation, analytics dashboard, and responsive design with light/dark/gray themes.

## Features

- **Rich Text Editor**: Quill.js-powered editor with custom toolbar for interactive elements
- **Interactive Content**: Embed quizzes, charts, videos, and PDFs directly in posts
- **AI Integration**: Google Gemini API for automatic category and tag generation
- **User Management**: Role-based authentication (admin/author) with secure login
- **Analytics Dashboard**: Track post views and quiz performance with Chart.js visualizations
- **Responsive Design**: Mobile-first design with Tailwind CSS and theme switching
- **Security**: Rate limiting, IP blocking, input sanitization, and CSRF protection
- **File Uploads**: Secure handling of PDFs, videos, and images

## Tech Stack

- **Backend**: Flask 3.0, SQLAlchemy, PostgreSQL (with psycopg3 driver)
- **Frontend**: Jinja2 templates, Tailwind CSS, Alpine.js, Quill.js, Chart.js, PDF.js
- **Authentication**: Flask-Login with Werkzeug password hashing
- **Security**: Flask-Limiter, Bleach sanitization
- **AI**: Google Gemini API for content categorization
- **Deployment**: Render (free tier compatible)
- **Python**: 3.13+ (modern async support, performance improvements)

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL database
- Google Gemini API key

### Local Development Setup

1. **Clone and setup virtual environment**:
   ```bash
   git clone <your-repo-url>
   cd interactive-blog
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize database**:
   ```bash
   flask db upgrade
   ```

5. **Create admin user**:
   ```bash
   python -c "
   from app import create_app, db
   from app.models import User

   app = create_app()
   with app.app_context():
       admin = User(username='admin', role='admin')
       admin.set_password('admin123')
       db.session.add(admin)
       db.session.commit()
       print('Admin user created: admin/admin123')
   "
   ```

6. **Run development server**:
   ```bash
   python run.py
   ```

7. **Access the application**:
   - Blog: http://localhost:5000
   - Login: http://localhost:5000/login
   - Editor: http://localhost:5000/editor (after login)

## Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Flask Configuration
SECRET_KEY=your-super-secret-key-change-in-production
FLASK_ENV=development

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/interactive_blog

# Gemini AI Configuration
GEMINI_API_KEY=your-gemini-api-key-here

# Optional: Redis for production rate limiting
REDIS_URL=redis://localhost:6379/0
```

### Required Environment Variables

- **SECRET_KEY**: Random secret key for Flask sessions (generate with `python -c "import secrets; print(secrets.token_hex(32))"`)
- **DATABASE_URL**: PostgreSQL connection string
- **GEMINI_API_KEY**: Google Gemini API key for AI tag generation

## Project Structure

```
interactive-blog/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── models.py                # Database models
│   ├── routes.py                # All application routes
│   ├── forms.py                 # WTForms definitions
│   ├── utils.py                 # Utility functions
│   ├── templates/               # Jinja2 templates
│   │   ├── base.html           # Base layout
│   │   ├── index.html          # Blog index
│   │   ├── post.html           # Single post view
│   │   ├── login.html          # Login form
│   │   ├── editor.html         # Rich text editor
│   │   ├── dashboard.html      # Analytics dashboard
│   │   └── admin.html          # Admin panel
│   └── static/                 # Static assets
│       ├── css/
│       │   └── tailwind.output.css
│       ├── js/
│       │   ├── app.js          # Main JavaScript
│       │   └── editor.js       # Editor-specific JS
│       └── uploads/            # User uploads
├── tests/                      # Test suite
├── config.py                   # Configuration classes
├── requirements.txt            # Python dependencies
├── run.py                      # Application entry point
├── tailwind.config.js          # Tailwind configuration
├── input.css                   # Tailwind source
├── Procfile                    # Render deployment
├── runtime.txt                 # Python version
└── README.md                   # This file
```

## Usage Guide

### Creating Content

1. **Login** with your admin/author credentials
2. **Navigate to Editor** (`/editor`)
3. **Write content** using the rich text editor
4. **Add interactive elements**:
   - Click quiz icon to add multiple-choice or true/false questions
   - Click chart icon to add data visualizations
   - Click video icon to embed videos
   - Click PDF icon to embed document viewers
5. **Save draft** or **publish** directly

### Shortcode System

The editor uses shortcodes that are automatically converted to interactive elements:

- `[quiz id=1]` → Interactive quiz form
- `[chart id=2]` → Chart.js visualization
- `[video id=3]` → HTML5 video player
- `[pdf id=4]` → PDF.js viewer in modal

### User Management

Admin users can:
- Create/manage other users
- View login attempt logs
- Access analytics data

### Analytics

The dashboard provides:
- Post view statistics over time
- Quiz attempt and success rates
- User engagement metrics

## Deployment to Render

### 1. Prepare Your Repository

1. **Push code to GitHub**:
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Set up Render PostgreSQL**:
   - Go to Render Dashboard → PostgreSQL
   - Create new PostgreSQL database
   - Note the connection string

### 2. Deploy Flask Application

1. **Create Render Web Service**:
   - Go to Render Dashboard → Web Services
   - Connect your GitHub repository
   - Configure service:
     - **Name**: `interactive-blog`
     - **Runtime**: `Python 3` (Render will use `runtime.txt` which specifies Python 3.12.7)
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn your_application.wsgi:application` or `gunicorn run:app`
     - ⚠️ **IMPORTANT**: 
       - If you see Python 3.13 in the build logs, Render isn't reading `runtime.txt` correctly
       - Go to Settings → Environment and ensure Python version is set to 3.12.7
       - Or manually set `PYTHON_VERSION=3.12.7` in environment variables

2. **Set Environment Variables** in Render:
   ```
   DATABASE_URL=postgresql://[your-connection-string]
   SECRET_KEY=[your-secret-key]
   GEMINI_API_KEY=[your-gemini-key]
   FLASK_ENV=production
   ```

3. **Deploy** the application

**⚠️ Troubleshooting Deployment Issues:**

**Database Driver Issue**: If you see `ImportError` with `psycopg2`:
- The app uses `psycopg[binary]` (psycopg3) which is compatible with Python 3.13+
- Make sure your environment has the correct database connection string

If you see `ModuleNotFoundError: No module named 'your_application'`:

**Solution 1 (Recommended)**: The repository now includes a `your_application/wsgi.py` module that works with Render's default command. This should work automatically.

**Solution 2**: If you want to use the Procfile instead:
1. **Check Render Dashboard Settings**:
   - Go to your Web Service → Settings
   - Scroll to "Start Command"
   - Ensure it's set to: `gunicorn run:app`
   - Save and redeploy

2. **Verify Procfile exists** in your repository root with:
   ```
   web: gunicorn run:app
   ```

**Solution 3**: Alternative start commands:
   - `gunicorn wsgi:app` (using the wsgi.py file)
   - `gunicorn your_application.wsgi:application` (using the workaround module)

### 3. Database Setup

After deployment, run database migrations:

```bash
# If you have shell access to Render
flask db upgrade

# Or create an admin user
python -c "
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    db.create_all()
    admin = User(username='admin', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
"
```

## Development Commands

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_models.py

# Run Flask shell
flask shell

# Database migrations
flask db migrate -m "Migration message"
flask db upgrade
flask db downgrade

# Compile Tailwind CSS (if using custom build)
npx tailwindcss -i input.css -o app/static/css/tailwind.output.css --watch
```

## API Endpoints

### Public Endpoints
- `GET /` - Blog index
- `GET /post/<slug>` - Single post view
- `GET /category/<category>` - Posts by category
- `GET /tag/<tag>` - Posts by tag

### Authentication
- `GET/POST /login` - User login
- `GET /logout` - User logout

### Protected Endpoints (require login)
- `GET /dashboard` - Analytics dashboard
- `GET /editor` - Post editor
- `POST /api/save_draft` - Auto-save drafts
- `POST /api/publish` - Publish posts

### Admin Endpoints (require admin role)
- `GET /admin/users` - User management
- `POST /admin/users/add` - Create user
- `GET /admin/logins` - Login logs

## Security Features

- **Rate Limiting**: 5 login attempts per 5 minutes per IP
- **IP Blocking**: Automatic blocking after 5 failed login attempts
- **Input Sanitization**: All user inputs sanitized with Bleach
- **CSRF Protection**: Enabled on all forms
- **Secure Passwords**: Werkzeug PBKDF2 hashing
- **Session Security**: Secure cookies in production

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest -m unit
pytest -m integration
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

For questions or issues:
- Check the [Issues](https://github.com/yourusername/interactive-blog/issues) page
- Create a new issue with detailed information
- Include error messages and steps to reproduce

## Roadmap

- [ ] Comment system for posts
- [ ] Social media sharing integration
- [ ] Advanced analytics and reporting
- [ ] Multi-author support enhancements
- [ ] Plugin system for custom interactive elements
- [ ] API for external integrations
