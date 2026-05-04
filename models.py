from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# Initialize the database
db = SQLAlchemy()

# Models

class User(UserMixin, db.Model):
    """
    User model for authentication.
    Stores common information like username, password, and role.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)  # Hashed password
    name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'admin', 'company', 'student'

    # Relationships (One-to-One with Student and Company)
    # uselist=False ensures One-to-One
    student_profile = db.relationship('Student', backref='user', uselist=False)
    company_profile = db.relationship('Company', backref='user', uselist=False)

class Student(db.Model):
    """
    Student model for storing academic details.
    Linked to User model via One-to-One relationship.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    roll_number = db.Column(db.String(50), unique=True, nullable=False)
    cgpa = db.Column(db.Float, nullable=False)
    department = db.Column(db.String(150), nullable=True) # Department name
    is_blacklisted = db.Column(db.Boolean, default=False)
    resume_link = db.Column(db.String(300), nullable=True) # Link to resume (optional)
    skills = db.Column(db.Text, nullable=True) # Comma-separated skills

    # Relationships (One-to-Many with Application)
    applications = db.relationship('Application', backref='student', lazy=True)

class Company(db.Model):
    """
    Company model for storing company details.
    Linked to User model via One-to-One relationship.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(50), default='pending')  # 'approved', 'pending', 'rejected'
    is_blacklisted = db.Column(db.Boolean, default=False)

    # Relationships (One-to-Many with Drive)
    drives = db.relationship('Drive', backref='company', lazy=True)

class Drive(db.Model):
    """
    Drive model represents a job posting by a company.
    """
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False, server_default='Default Drive') # e.g., 'Drive 1'
    job_role = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(150), nullable=True) # Location for drive
    eligibility_cgpa = db.Column(db.Float, nullable=False)
    salary = db.Column(db.Float, nullable=False, default=0.0) # Package in LPA
    deadline = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default='active')  # 'active', 'closed'

    # Relationships (One-to-Many with Application)
    applications = db.relationship('Application', backref='drive', lazy=True)

class Application(db.Model):
    """
    Application model represents a student applying to a drive.
    Links Student and Drive (Many-to-Many logic via association table, but here an explicit model).
    """
    id = db.Column(db.Integer, primary_key=True)
    drive_id = db.Column(db.Integer, db.ForeignKey('drive.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    applied_on = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='applied')  # 'applied', 'accepted', 'rejected'

    # Unique constraint to prevent duplicate applications
    __table_args__ = (db.UniqueConstraint('drive_id', 'student_id', name='unique_application'),)
