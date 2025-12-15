"""
ASGI entrypoint for Uvicorn/Gunicorn.

This module exists so deployment configs can reference a stable symbol:
  - `company_researcher.api.main:app`
"""

from .app import get_app

app = get_app()

__all__ = ["app"]


