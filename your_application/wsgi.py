"""
WSGI entry point for Render deployment.
This file exists to work with Render's default 'gunicorn your_application.wsgi' command.
"""
from run import app

# Export the app for gunicorn
application = app

if __name__ == "__main__":
    app.run()
