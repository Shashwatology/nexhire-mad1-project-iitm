from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, User, Company, Student, Drive, Application
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
        
    search_query = request.args.get('search', '').strip()
    
    # Base queries
    registered_companies_query = Company.query.join(User).filter(Company.status=='approved', Company.is_blacklisted==False)
    registered_students_query = Student.query.join(User).filter(Student.is_blacklisted==False)
    pending_companies_query = Company.query.join(User).filter(Company.status=='pending')
    ongoing_drives_query = Drive.query.filter_by(status='active')
    applications_query = Application.query.join(Student).join(User)

    if search_query:
        # Search in company names
        registered_companies_query = registered_companies_query.filter(User.name.ilike(f'%{search_query}%'))
        # Search in student names or roll numbers
        registered_students_query = registered_students_query.filter(
            (User.name.ilike(f'%{search_query}%')) | (Student.roll_number.ilike(f'%{search_query}%'))
        )
        # Search in pending company names
        pending_companies_query = pending_companies_query.filter(User.name.ilike(f'%{search_query}%'))
        # Search in drive names or job roles
        ongoing_drives_query = ongoing_drives_query.filter(
            (Drive.name.ilike(f'%{search_query}%')) | (Drive.job_role.ilike(f'%{search_query}%'))
        )
        # Search in applications by student name or drive name
        applications_query = applications_query.filter(
            (User.name.ilike(f'%{search_query}%')) | (Application.drive.has(Drive.name.ilike(f'%{search_query}%')))
        )

    registered_companies = registered_companies_query.all()
    registered_students = registered_students_query.all()
    pending_companies = pending_companies_query.all()
    ongoing_drives = ongoing_drives_query.all()
    applications = applications_query.all()
    
    return render_template('admin/dashboard.html', 
                           registered_companies=registered_companies, 
                           registered_students=registered_students,
                           pending_companies=pending_companies,
                           ongoing_drives=ongoing_drives,
                           applications=applications)

@admin_bp.route('/approve_company/<int:company_id>')
@login_required
def approve_company(company_id):
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
        
    company = Company.query.get_or_404(company_id)
    company.status = 'approved'
    db.session.commit()
    flash(f'Company {company.user.name} approved.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/reject_company/<int:company_id>')
@login_required
def reject_company(company_id):
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
        
    company = Company.query.get_or_404(company_id)
    company.status = 'rejected'
    db.session.commit()
    flash(f'Company {company.user.name} rejected.', 'danger')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/blacklist_company/<int:company_id>')
@login_required
def blacklist_company(company_id):
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
        
    company = Company.query.get_or_404(company_id)
    company.is_blacklisted = True
    company.status = 'rejected' # Also reject them technically or just blacklist
    db.session.commit()
    flash(f'Company {company.user.name} blacklisted.', 'warning')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/blacklist_student/<int:student_id>')
@login_required
def blacklist_student(student_id):
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
        
    student = Student.query.get_or_404(student_id)
    student.is_blacklisted = True
    db.session.commit()
    flash(f'Student {student.user.name} blacklisted.', 'warning')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/complete_drive/<int:drive_id>')
@login_required
def complete_drive(drive_id):
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
        
    drive = Drive.query.get_or_404(drive_id)
    drive.status = 'closed'
    db.session.commit()
    flash(f'Drive {drive.name} marked as complete.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/drive_details/<int:drive_id>')
@login_required
def drive_details(drive_id):
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
    drive = Drive.query.get_or_404(drive_id)
    return render_template('admin/drive_details.html', drive=drive)

@admin_bp.route('/student_application/<int:app_id>')
@login_required
def student_application(app_id):
    if current_user.role != 'admin':
        return redirect(url_for('auth.login'))
    application = Application.query.get_or_404(app_id)
    return render_template('admin/student_application.html', application=application)
