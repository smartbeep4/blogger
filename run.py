import os
from app import create_app

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

if __name__ == '__main__':
    # Run the development server
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config.get('DEBUG', False)
    )
