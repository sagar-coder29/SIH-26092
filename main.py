# Copyright 2024
# Directory: yt-rag/main.py

"""
Legacy entry point for backward compatibility.
The main application is now in app/main.py
"""

from app.main import app

# Re-export the app for uvicorn
__all__ = ["app"]
