"""
WSGI entry point for production deployment.
This file can be used if Render doesn't detect the Procfile.
"""
import os
from run import app

if __name__ == "__main__":
    app.run()
