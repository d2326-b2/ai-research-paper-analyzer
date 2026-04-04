"""
HypoGen Database Module
Handles all SQLAlchemy ORM models and database configuration

This module defines:
- User model with encrypted password storage
- Database initialization and configuration
- Password hashing and verification using bcrypt

Author: Your Name
Date: 2024
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import bcrypt

# Initialize SQLAlchemy ORM
db = SQLAlchemy()


class User(UserMixin, db.Model):
    """
    User model for authentication and session management.
    
    Attributes:
        id (int): Primary key, auto-incremented user ID
        name (str): User's full name (100 chars max)
        email (str): User's email, must be unique
        password (str): Bcrypt-hashed password (200 chars for hash storage)
    
    Methods:
        set_password(password): Hashes and stores password using bcrypt
        check_password(password): Verifies password against stored hash
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def set_password(self, password: str) -> None:
        """
        Hash and store password using bcrypt with salt.
        
        Args:
            password (str): Plaintext password to hash
        """
        hashed = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        )
        self.password = hashed.decode('utf-8')

    def check_password(self, password: str) -> bool:
        """
        Verify plaintext password against stored hash.
        
        Args:
            password (str): Plaintext password to verify
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password.encode('utf-8')
        )
