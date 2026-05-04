import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import app
from models import db, User, Company, Drive, Student, Application

def seed_database():
    with app.app_context():
        print("Clearing database...")
        db.drop_all()
        db.create_all()

        print("Seeding Admin...")
        admin = User(
            username='admin', 
            password=generate_password_hash('admin', method='scrypt'), 
            name='Placement Admin', 
            role='admin'
        )
        db.session.add(admin)

        print("Seeding Companies...")
        companies_data = [
            {"username": "technova", "name": "TechNova Solutions", "desc": "Leading provider of AI and Data Science solutions enterprise software.", "industry": "IT & Software"},
            {"username": "datasys", "name": "DataSys Global", "desc": "Multinational consulting and analytics firm.", "industry": "Consulting"},
            {"username": "fintechio", "name": "Fintech.io", "desc": "Modern banking solutions and blockchain technology.", "industry": "Finance"},
            {"username": "healthcorp", "name": "HealthCorp Systems", "desc": "Software solutions for the healthcare and pharmaceutical sector.", "industry": "Healthcare"},
            {"username": "edutech", "name": "EduTech Innovations", "desc": "Pioneers in digital learning management systems.", "industry": "Education"}
        ]

        company_objects = []
        for i, c in enumerate(companies_data):
            user = User(
                username=c["username"],
                password=generate_password_hash('password', method='scrypt'),
                name=c["name"],
                role='company'
            )
            db.session.add(user)
            db.session.flush() # To get user.id
            
            company = Company(
                user_id=user.id,
                description=c["desc"],
                industry=c["industry"],
                status='approved'
            )
            db.session.add(company)
            company_objects.append(company)

        print("Seeding Students...")
        students_data = [
            {"username": "arjun_kumar", "name": "Arjun Kumar"},
            {"username": "neha_sharma", "name": "Neha Sharma"},
            {"username": "rohit_singh", "name": "Rohit Singh"},
            {"username": "priya_desai", "name": "Priya Desai"},
            {"username": "vikram_rathore", "name": "Vikram Rathore"}
        ]
        
        skills_pool = ['Python', 'Java', 'C++', 'JavaScript', 'React', 'Node.js', 'SQL', 'MongoDB', 'AWS', 'Docker', 'Machine Learning', 'Data Analysis']
        
        student_objects = []
        for i, s in enumerate(students_data):
            user = User(
                username=s["username"],
                password=generate_password_hash('password', method='scrypt'),
                name=s["name"],
                role='student'
            )
            db.session.add(user)
            db.session.flush()
            
            sample_skills = random.sample(skills_pool, random.randint(3, 6))
            dept_pool = ['Computer Science and Engineering', 'Electronics and Communication', 'Mechanical Engineering', 'Data Science']
            
            student = Student(
                user_id=user.id,
                roll_number=f"24DS{1000 + i}",
                cgpa=round(random.uniform(6.5, 9.8), 2),
                department=random.choice(dept_pool),
                skills=", ".join(sample_skills)
            )
            db.session.add(student)
            student_objects.append(student)


        print("Seeding Drives...")
        job_roles = ['Software Engineer', 'Data Analyst', 'Frontend Developer', 'Backend Developer', 'Product Manager', 'ML Engineer']
        
        drive_objects = []
        for j in range(15):
            company = random.choice(company_objects)
            job = random.choice(job_roles)
            locations = ['Chennai', 'Bangalore', 'Hyderabad', 'Pune', 'Remote']
            
            drive = Drive(
                company_id=company.id,
                name=f"Drive {j+1}",
                job_role=job,
                description=f"We are looking for a highly motivated {job} to join our dynamic team and build scalable enterprise solutions.",
                location=random.choice(locations),
                eligibility_cgpa=round(random.uniform(6.0, 8.5), 1),
                salary=round(random.uniform(5.0, 25.0), 1),
                deadline=datetime.utcnow() + timedelta(days=random.randint(5, 30)),
                status='active'
            )
            db.session.add(drive)
            drive_objects.append(drive)

        print("Seeding Applications...")
        db.session.commit() # Commit drives first so they have IDs
        
        for student in student_objects:
            # Each student applies to 2-5 random drives
            num_applications = random.randint(2, 5)
            # Find eligible drives
            eligible_drives = [d for d in drive_objects if student.cgpa >= d.eligibility_cgpa]
            
            if eligible_drives:
                drives_to_apply = random.sample(eligible_drives, min(num_applications, len(eligible_drives)))
                for drive in drives_to_apply:
                    status = random.choice(['applied', 'shortlisted', 'waiting', 'rejected']) # Weight towards 'applied' can be added if needed
                    app_record = Application(
                        student_id=student.id,
                        drive_id=drive.id,
                        status=status,
                        applied_on=datetime.utcnow() - timedelta(days=random.randint(1, 10))
                    )
                    db.session.add(app_record)

        db.session.commit()
        print("Database seeding completed successfully!")
        print("Credentials:")
        print("  Admin: admin / admin")
        print("  Companies: technova, datasys, etc. / password")
        print("  Students: arjun_kumar, neha_sharma, etc. / password")

if __name__ == '__main__':
    seed_database()
