from flask_sqlalchemy import SQLAlchemy
import sys
import os

# Add parent directory to path to import logging utilities
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.logging.config import get_logger

# Create module logger
logger = get_logger(__name__)

db = SQLAlchemy()

# Import models after db is defined to avoid circular imports
from .breed import Breed
from .dog import Dog

# Initialize function to be called from app.py
def init_db(app):
    logger.info("Initializing database connection")
    
    try:
        db.init_app(app)
        logger.debug("SQLAlchemy initialized with app context")
        
        # Create tables when initializing
        with app.app_context():
            logger.debug("Creating database tables if they don't exist")
            db.create_all()
            logger.info("Database tables verified/created successfully")
    except Exception as e:
        logger.critical(f"Database initialization failed: {str(e)}", exc_info=True)
        raise