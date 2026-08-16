from app import app, db, User

with app.app_context():
    updated = User.query.filter(User.approved.is_(None)).update({"approved": True})
    db.session.commit()
    print(f"Updated {updated} user(s).")