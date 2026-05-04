from flask import Flask, render_template, redirect, url_for
from config import Config
from models import db, User, Company, Drive, Student
from flask_login import LoginManager, current_user
from werkzeug.security import generate_password_hash

# Initialize Flask App
app = Flask(__name__)
app.config.from_object(Config)

# Initialize Extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Import Blueprints (We will create these files next)
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.student import student_bp
from routes.company import company_bp
from routes.api import api_bp

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(student_bp, url_prefix='/student')
app.register_blueprint(company_bp, url_prefix='/company')
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def home():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'company':
            return redirect(url_for('company.dashboard'))
        elif current_user.role == 'student':
            return redirect(url_for('student.dashboard'))
    return render_template('landing.html', stats={'companies': Company.query.count(), 'drives': Drive.query.count(), 'students': Student.query.count()})

# Create database and tables automatically on startup
with app.app_context():
    db.create_all()
    print("Programmatic database creation verified/completed.")

def create_admin():
    """
    Creates the default admin user if it doesn't exist.
    """
    with app.app_context():
        # check if admin exists
        if not User.query.filter_by(username='admin').first():
            hashed_pw = generate_password_hash('admin', method='scrypt') 
            admin = User(username='admin', password=hashed_pw, name='Admin Role', role='admin')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created!")

if __name__ == '__main__':
    create_admin()
    app.run(debug=True)
