from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Company, Drive, Application, Student
from datetime import datetime
from datetime import datetime

company_bp = Blueprint('company', __name__)

@company_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'company':
        return redirect(url_for('auth.login'))
        
    company = Company.query.filter_by(user_id=current_user.id).first()
    
    if company.status != 'approved':
        return render_template('company/pending.html') # Need to create this or handle in dashboard
        
    upcoming_drives = Drive.query.filter_by(company_id=company.id, status='active').all()
    closed_drives = Drive.query.filter_by(company_id=company.id, status='closed').all()
    
    return render_template('company/dashboard.html', upcoming_drives=upcoming_drives, closed_drives=closed_drives, company=company)

@company_bp.route('/create_drive', methods=['GET', 'POST'])
@login_required
def create_drive():
    if current_user.role != 'company':
        return redirect(url_for('auth.login'))
        
    company = Company.query.filter_by(user_id=current_user.id).first()
    if company.status != 'approved':
        flash('Your company account is not approved yet.', 'warning')
        return redirect(url_for('company.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name')
        job_role = request.form.get('job_role')
        description = request.form.get('description')
        location = request.form.get('location')
        eligibility_cgpa = float(request.form.get('eligibility_cgpa'))
        salary = float(request.form.get('salary', 0.0))
        deadline_str = request.form.get('deadline')
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
        
        new_drive = Drive(
            company_id=company.id,
            name=name,
            job_role=job_role,
            description=description,
            location=location,
            eligibility_cgpa=eligibility_cgpa,
            salary=salary,
            deadline=deadline
        )
        db.session.add(new_drive)
        db.session.commit()
        
        flash('Drive created successfully!', 'success')
        return redirect(url_for('company.dashboard'))
        
    return render_template('company/create_drive.html')

@company_bp.route('/mark_complete/<int:drive_id>')
@login_required
def mark_complete(drive_id):
    if current_user.role != 'company':
        return redirect(url_for('auth.login'))
        
    drive = Drive.query.get_or_404(drive_id)
    if drive.company.user_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('company.dashboard'))
        
    drive.status = 'closed'
    db.session.commit()
    flash(f'Drive {drive.name} marked as complete.', 'success')
    return redirect(url_for('company.dashboard'))

@company_bp.route('/drive/<int:drive_id>/applications')
@login_required
def view_applications(drive_id):
    if current_user.role != 'company':
        return redirect(url_for('auth.login'))
        
    drive = Drive.query.get_or_404(drive_id)
    # Ensure this drive belongs to the logged-in company
    if drive.company.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('company.dashboard'))
        
    applications = Application.query.filter_by(drive_id=drive_id).all()
    return render_template('company/view_applications.html', drive=drive, applications=applications)

@company_bp.route('/application/<int:app_id>/review', methods=['GET', 'POST'])
@login_required
def review_application(app_id):
    if current_user.role != 'company':
        return redirect(url_for('auth.login'))
        
    application = Application.query.get_or_404(app_id)
    # Verify ownership
    if application.drive.company.user_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('company.dashboard'))
        
    if request.method == 'POST':
        status = request.form.get('status')
        if status in ['shortlisted', 'waiting', 'rejected']:
            application.status = status
            db.session.commit()
            flash(f'Application status updated to {status}.', 'success')
            return redirect(url_for('company.view_applications', drive_id=application.drive_id))
    
    return render_template('company/review_application.html', application=application)
