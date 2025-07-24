"""
API package for Smart Home System
"""

API_VERSION = "v1"

from src.api.routes import create_flask_app

__all__ = ["create_flask_app", "API_VERSION"]