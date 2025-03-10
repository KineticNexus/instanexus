"""
Web Interface Module - Flask-based web UI for managing the Instagram bot
"""

from .app import create_app
from .routes import register_routes
from .auth import login_required, current_user

__all__ = ['create_app', 'register_routes', 'login_required', 'current_user']