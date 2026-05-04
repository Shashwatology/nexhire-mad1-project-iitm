from flask import Blueprint, jsonify
from models import Drive, Company, Student, User

api_bp = Blueprint('api', __name__)

@api_bp.route('/drives')
def get_drives():
    """Returns a JSON list of all active placement drives."""
    drives = Drive.query.filter_by(status='active').all()
    
    drives_data = []
    for drive in drives:
        drives_data.append({
            'id': drive.id,
            'name': drive.name,
            'company': drive.company.user.name,
            'role': drive.job_role,
            'location': drive.location,
            'salary_lpa': drive.salary,
            'eligibility_cgpa': drive.eligibility_cgpa,
            'deadline': drive.deadline.strftime('%Y-%m-%d')
        })
        
    return jsonify({
        'status': 'success',
        'count': len(drives_data),
        'drives': drives_data
    })

@api_bp.route('/companies')
def get_companies():
    """Returns a JSON list of all approved companies."""
    companies = Company.query.filter_by(status='approved').all()
    
    companies_data = []
    for company in companies:
        companies_data.append({
            'id': company.id,
            'name': company.user.name,
            'industry': company.industry,
            'description': company.description
        })
        
    return jsonify({
        'status': 'success',
        'count': len(companies_data),
        'companies': companies_data
    })

@api_bp.route('/stats')
def get_stats():
    """Returns a JSON summary of platform statistics."""
    total_companies = Company.query.filter_by(status='approved').count()
    active_drives = Drive.query.filter_by(status='active').count()
    registered_students = Student.query.count()
    
    return jsonify({
        'status': 'success',
        'data': {
            'approved_companies': total_companies,
            'active_drives': active_drives,
            'registered_students': registered_students
        }
    })
