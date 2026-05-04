from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Student, Company

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'student':
            return redirect(url_for('student.dashboard'))
        elif current_user.role == 'company':
            return redirect(url_for('company.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'student':
                return redirect(url_for('student.dashboard'))
            elif user.role == 'company':
                return redirect(url_for('company.dashboard'))
        else:
            flash('Invalid username or password', 'danger')
            
    return render_template('index.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        role = request.form.get('role') # 'student' or 'company'
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('auth.register'))
            
        hashed_pw = generate_password_hash(password, method='scrypt')
        new_user = User(username=username, password=hashed_pw, name=name, role=role)
        db.session.add(new_user)
        db.session.commit()
        
        # Create specific profile based on role
        if role == 'student':
            # Ask for basic info and create the related row with defaults.
            pass
        elif role == 'company':
            pass
            
        # Re-fetching needed to get ID? yes.
        # Commit already done.
        
        if role == 'student':
            new_student = Student(user_id=new_user.id, roll_number=username, cgpa=0.0) # Placeholder
            db.session.add(new_student)
        elif role == 'company':
            new_company = Company(user_id=new_user.id, status='pending')
            db.session.add(new_company)
            
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
