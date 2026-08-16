from app import app, db, User, StudentProfile

with app.app_context():
    student_users = User.query.filter_by(role="student").all()
    fixed = []
    for u in student_users:
        if not StudentProfile.query.filter_by(user_id=u.id).first():
            db.session.add(StudentProfile(user_id=u.id))
            fixed.append(u.name)
    db.session.commit()
    print(f"Created {len(fixed)} missing StudentProfile rows: {fixed}")