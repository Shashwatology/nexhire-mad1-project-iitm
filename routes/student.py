from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Student, Drive, Application, Company, User

student_bp = Blueprint('student', __name__)

@student_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'student':
        return redirect(url_for('auth.login'))
        
    student = Student.query.filter_by(user_id=current_user.id).first()
    search_query = request.args.get('search', '').strip()
    
    # 1. Organizations List (Approved Companies)
    organizations_query = Company.query.join(User).filter(Company.status=='approved')
    if search_query:
        organizations_query = organizations_query.filter(User.name.ilike(f'%{search_query}%'))
    
    organizations = organizations_query.all()
    
    # 2. Applied Drives List
    my_applications = Application.query.filter_by(student_id=student.id).all()
    
    return render_template('student/dashboard.html', 
                           organizations=organizations, 
                           my_applications=my_applications,
                           student=student)

@student_bp.route('/company/<int:company_id>')
@login_required
def company_overview(company_id):
    if current_user.role != 'student':
        return redirect(url_for('auth.login'))
        
    company = Company.query.get_or_404(company_id)
    # Active drives for this company
    current_drives = Drive.query.filter_by(company_id=company.id, status='active').all()
    
    return render_template('student/company_overview.html', company=company, current_drives=current_drives)

@student_bp.route('/drive/<int:drive_id>')
@login_required
def drive_details(drive_id):
    if current_user.role != 'student':
        return redirect(url_for('auth.login'))
        
    drive = Drive.query.get_or_404(drive_id)
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    # Check if already applied
    has_applied = Application.query.filter_by(student_id=student.id, drive_id=drive_id).first() is not None
    is_eligible = student.cgpa >= drive.eligibility_cgpa
    
    return render_template('student/drive_details.html', drive=drive, has_applied=has_applied, is_eligible=is_eligible)

@student_bp.route('/history')
@login_required
def history():
    if current_user.role != 'student':
        return redirect(url_for('auth.login'))
        
    student = Student.query.filter_by(user_id=current_user.id).first()
    applications = Application.query.filter_by(student_id=student.id).all()
    
    return render_template('student/history.html', applications=applications)

@student_bp.route('/apply/<int:drive_id>', methods=['POST'])
@login_required
def apply(drive_id):
    if current_user.role != 'student':
        return redirect(url_for('auth.login'))
        
    student = Student.query.filter_by(user_id=current_user.id).first()
    drive = Drive.query.get_or_404(drive_id)
    
    # Check Eligibility (CGPA)
    if student.cgpa < drive.eligibility_cgpa:
        flash(f'Not eligible! Required CGPA: {drive.eligibility_cgpa}', 'danger')
        return redirect(url_for('student.dashboard'))
        
    # Check Duplicate
    existing_application = Application.query.filter_by(student_id=student.id, drive_id=drive_id).first()
    if existing_application:
        flash('You have already applied to this drive.', 'warning')
        return redirect(url_for('student.dashboard'))
        
    # Create Application
    new_application = Application(student_id=student.id, drive_id=drive_id)
    db.session.add(new_application)
    db.session.commit()
    
    flash('Applied successfully!', 'success')
    return redirect(url_for('student.dashboard'))

@student_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if current_user.role != 'student':
        return redirect(url_for('auth.login'))
        
    student = Student.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        try:
            student.cgpa = float(request.form.get('cgpa'))
            student.skills = request.form.get('skills')
            student.resume_link = request.form.get('resume_link')
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('student.dashboard'))
        except ValueError:
            flash('Invalid Input!', 'danger')
            
    return render_template('student/profile.html', student=student)
