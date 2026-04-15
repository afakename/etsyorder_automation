"""
database.py
SQLAlchemy instance — imported by models.py and app.py.
Kept separate to avoid circular imports.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
