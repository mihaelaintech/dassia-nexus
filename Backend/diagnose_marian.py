from app import app, User, MentorProfile

with app.app_context():
    user = User.query.filter(User.name.ilike("%Marian%")).first()

    if not user:
        print("No user found matching 'Marian'.")
    else:
        print(f"User ID: {user.id}")
        print(f"Name: {user.name}")
        print(f"Email: {user.email}")
        print(f"Role: {user.role}")
        print(f"Approved: {user.approved}")

        profile = MentorProfile.query.filter_by(user_id=user.id).first()
        if profile:
            print(f"MentorProfile ID: {profile.id}")
            print(f"Interview status: {profile.interview_status}")
        else:
            print("No MentorProfile found for this user.")