from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

# Initialize SQLAlchemy
db = SQLAlchemy()

# Define the User model
class User(UserMixin, db.Model):
    __tablename__ = 'users'  # Table name in the database
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    vehicle_number = db.Column(db.String(100), unique=True, nullable=False)  # Unique identifier
    name = db.Column(db.String(100), nullable=False)  # User's name
    email = db.Column(db.String(100), unique=True, nullable=False)  # User's email
    password = db.Column(db.String(200), nullable=False)  # Hashed password
