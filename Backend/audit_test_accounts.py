from app import app, db, User, MentorProfile, StudentProfile

with app.app_context():
    print("=== Mentors: approved=True but interview not Completed ===")
    rows = User.query.filter_by(role="mentor", approved=True).join(
        MentorProfile, MentorProfile.user_id == User.id
    ).filter(MentorProfile.interview_status != "Completed").all()
    for u in rows:
        m = MentorProfile.query.filter_by(user_id=u.id).first()
        print(f"  id={u.id} {u.name} <{u.email}> interview_status={m.interview_status}")
    if not rows:
        print("  none")

    print()
    print("=== Mentors: interview Completed but approved=False ===")
    rows = User.query.filter_by(role="mentor", approved=False).join(
        MentorProfile, MentorProfile.user_id == User.id
    ).filter(MentorProfile.interview_status == "Completed").all()
    for u in rows:
        print(f"  id={u.id} {u.name} <{u.email}>")
    if not rows:
        print("  none")

    print()
    print("=== Mentors: interview_scheduled_at set but status still Not Scheduled ===")
    rows = MentorProfile.query.filter(
        MentorProfile.interview_scheduled_at.isnot(None),
        MentorProfile.interview_status == "Not Scheduled"
    ).all()
    for m in rows:
        u = User.query.get(m.user_id)
        print(f"  mentor_id={m.id} user_id={m.user_id} {u.name if u else '?'} scheduled_at={m.interview_scheduled_at}")
    if not rows:
        print("  none")

    print()
    print("=== Users with role=mentor but no MentorProfile row ===")
    mentor_users = User.query.filter_by(role="mentor").all()
    orphans = [u for u in mentor_users if not MentorProfile.query.filter_by(user_id=u.id).first()]
    for u in orphans:
        print(f"  id={u.id} {u.name} <{u.email}> approved={u.approved}")
    if not orphans:
        print("  none")

    print()
    print("=== Users with role=student but no StudentProfile row ===")
    student_users = User.query.filter_by(role="student").all()
    orphans = [u for u in student_users if not StudentProfile.query.filter_by(user_id=u.id).first()]
    for u in orphans:
        print(f"  id={u.id} {u.name} <{u.email}>")
    if not orphans:
        print("  none")