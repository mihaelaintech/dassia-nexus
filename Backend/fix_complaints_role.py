from app import app, db, User

with app.app_context():
    user = User.query.filter_by(email="complaints123@example.com").first()

    if not user:
        print("No user found with that email.")
    else:
        user.role = "complaints"
        db.session.commit()
        print(f"Updated {user.email} to role: {user.role}")