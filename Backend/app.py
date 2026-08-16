import os
import secrets
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///dassia.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-fallback-key-change-me")

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "png", "jpg", "jpeg"}

db = SQLAlchemy(app)
migrate = Migrate(app, db)

TOKEN_LIFETIME_HOURS = 8


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    role = db.Column(db.String(20))  # "student", "mentor", "manager", or "complaints"
    password_hash = db.Column(db.String(255))
    approved = db.Column(db.Boolean, default=True)


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


class MentorProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    expertise = db.Column(db.String(200))
    bio = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=True)

    # Day 10: extended mentor application fields
    university = db.Column(db.String(200))
    qualification_level = db.Column(db.String(100))
    graduation_year = db.Column(db.Integer)
    personal_statement = db.Column(db.Text)
    interview_scheduled_at = db.Column(db.DateTime, nullable=True)
    interview_status = db.Column(db.String(20), default="Not Scheduled")  # Not Scheduled / Scheduled / Completed


class MentorCredential(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey("mentor_profile.id"), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # "qualification" or "certification"
    name = db.Column(db.String(200), nullable=False)
    institution = db.Column(db.String(200))
    year = db.Column(db.Integer)


class MentorSkill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey("mentor_profile.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)


class MentorJobHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey("mentor_profile.id"), nullable=False)
    job_title = db.Column(db.String(150), nullable=False)
    employer = db.Column(db.String(150), nullable=False)
    start_year = db.Column(db.Integer)
    end_year = db.Column(db.Integer, nullable=True)
    is_current = db.Column(db.Boolean, default=False)


class StudentProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    university = db.Column(db.String(200))
    course = db.Column(db.String(200))
    year_of_study = db.Column(db.String(50))
    bio = db.Column(db.Text)


class StudentSkill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student_profile.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)


class StudentInterest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student_profile.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)


class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submitted_by_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    submitted_by_name = db.Column(db.String(100))
    submitted_by_role = db.Column(db.String(20))
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="Open")  # "Open" or "Resolved"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class FeedbackRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100))
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default="Pending")
    mentor_id = db.Column(db.Integer, db.ForeignKey("mentor_profile.id"), nullable=True)
    student_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)


class FeedbackComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("feedback_request.id"))
    mentor_id = db.Column(db.Integer, db.ForeignKey("mentor_profile.id"))
    comment = db.Column(db.Text)


class AuthToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)


VALID_STATUSES = ["Pending", "In Progress", "Completed"]

ALLOWED_TRANSITIONS = {
    "Pending": ["In Progress"],
    "In Progress": ["Completed", "Pending"],
    "Completed": []
}


def get_json_body():
    return request.get_json(silent=True) or {}


def require_fields(data, fields):
    return [f for f in fields if not data.get(f)]


def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify({"message": "Missing or invalid Authorization header"}), 401

        token_value = auth_header.split(" ", 1)[1]
        token_row = AuthToken.query.filter_by(token=token_value).first()

        if not token_row or token_row.expires_at < datetime.utcnow():
            return jsonify({"message": "Invalid or expired token"}), 401

        request.current_user = User.query.get(token_row.user_id)

        if not request.current_user:
            return jsonify({"message": "User account no longer exists"}), 401

        return f(*args, **kwargs)
    return wrapper


def require_role(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if request.current_user.role not in roles:
                return jsonify({"message": f"This action requires one of the following roles: {', '.join(roles)}"}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator


@app.errorhandler(404)
def not_found(e):
    return jsonify({"message": "Resource not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"message": "Internal server error"}), 500


@app.route("/")
def home():
    return jsonify({"message": "DASSIA Academic Mentoring Platform API is running"})


@app.route("/create-db")
def create_db():
    db.create_all()
    return jsonify({"message": "Database tables created successfully"})


@app.route("/register", methods=["POST"])
def register_user():
    data = get_json_body()
    missing = require_fields(data, ["name", "email", "role", "password"])

    if missing:
        return jsonify({"message": f"Missing required fields: {', '.join(missing)}"}), 400

    if data["role"] not in ("student", "mentor", "manager", "complaints"):
        return jsonify({"message": "role must be 'student', 'mentor', 'manager', or 'complaints'"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "A user with this email already exists"}), 409

    new_user = User(
        name=data["name"],
        email=data["email"],
        role=data["role"],
        password_hash=generate_password_hash(data["password"]),
        approved=(data["role"] != "mentor")
    )

    db.session.add(new_user)
    db.session.commit()

    if new_user.role == "mentor":
        mentor_profile = MentorProfile(
            name=new_user.name,
            expertise=data.get("expertise"),
            bio=data.get("bio"),
            user_id=new_user.id
        )
        db.session.add(mentor_profile)
        db.session.commit()

    if new_user.role == "student":
        student_profile = StudentProfile(
            user_id=new_user.id,
            university=data.get("university"),
            course=data.get("course"),
            year_of_study=data.get("year_of_study"),
            bio=data.get("bio"),
        )
        db.session.add(student_profile)
        db.session.commit()

    return jsonify({
        "message": "User created successfully",
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "role": new_user.role
        }
    }), 201


@app.route("/login", methods=["POST"])
def login():
    data = get_json_body()
    missing = require_fields(data, ["email", "password"])

    if missing:
        return jsonify({"message": f"Missing required fields: {', '.join(missing)}"}), 400

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not user.password_hash or not check_password_hash(user.password_hash, data["password"]):
        return jsonify({"message": "Invalid email or password"}), 401

    token_value = secrets.token_hex(32)
    expires_at = datetime.utcnow() + timedelta(hours=TOKEN_LIFETIME_HOURS)

    db.session.add(AuthToken(token=token_value, user_id=user.id, expires_at=expires_at))
    db.session.commit()

    return jsonify({
        "token": token_value,
        "expires_at": expires_at.isoformat(),
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }), 200


@app.route("/logout", methods=["POST"])
@require_auth
def logout():
    auth_header = request.headers.get("Authorization", "")
    token_value = auth_header.split(" ", 1)[1]

    AuthToken.query.filter_by(token=token_value).delete()
    db.session.commit()

    return jsonify({"message": "Logged out successfully"}), 200


@app.route("/me", methods=["GET"])
@require_auth
def me():
    user = request.current_user

    response = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "approved": user.approved
    }

    if user.role == "mentor":
        mentor = MentorProfile.query.filter_by(user_id=user.id).first()
        response["mentor_id"] = mentor.id if mentor else None

    return jsonify(response), 200


@app.route("/users", methods=["GET"])
@require_auth
def get_users():
    users = User.query.all()

    result = [{
        "id": u.id,
        "name": u.name,
        "email": u.email,
        "role": u.role
    } for u in users]

    return jsonify(result)


@app.route("/mentors", methods=["POST"])
@require_auth
@require_role("mentor")
def create_mentor():
    data = get_json_body()
    missing = require_fields(data, ["name"])

    if missing:
        return jsonify({"message": f"Missing required fields: {', '.join(missing)}"}), 400

    if MentorProfile.query.filter_by(user_id=request.current_user.id).first():
        return jsonify({"message": "This user already has a mentor profile"}), 409

    new_mentor = MentorProfile(
        name=data["name"],
        expertise=data.get("expertise"),
        bio=data.get("bio"),
        user_id=request.current_user.id
    )

    db.session.add(new_mentor)
    db.session.commit()

    return jsonify({
        "message": "Mentor profile created successfully",
        "mentor": {
            "id": new_mentor.id,
            "name": new_mentor.name,
            "expertise": new_mentor.expertise,
            "bio": new_mentor.bio
        }
    }), 201


@app.route("/mentors/<int:mentor_id>", methods=["PUT"])
@require_auth
@require_role("mentor")
def update_mentor(mentor_id):
    mentor = MentorProfile.query.get(mentor_id)

    if not mentor:
        return jsonify({"message": "Mentor profile not found"}), 404

    if mentor.user_id != request.current_user.id:
        return jsonify({"message": "You can only edit your own mentor profile"}), 403

    data = get_json_body()
    mentor.name = data.get("name", mentor.name)
    mentor.expertise = data.get("expertise", mentor.expertise)
    mentor.bio = data.get("bio", mentor.bio)

    db.session.commit()

    return jsonify({
        "message": "Mentor profile updated successfully",
        "mentor": {
            "id": mentor.id,
            "name": mentor.name,
            "expertise": mentor.expertise,
            "bio": mentor.bio
        }
    }), 200


@app.route("/mentors/<int:mentor_id>/profile-details", methods=["PUT"])
@require_auth
@require_role("mentor")
def update_mentor_profile_details(mentor_id):
    mentor = MentorProfile.query.get(mentor_id)

    if not mentor:
        return jsonify({"message": "Mentor profile not found"}), 404

    if mentor.user_id != request.current_user.id:
        return jsonify({"message": "You can only edit your own mentor profile"}), 403

    data = get_json_body()
    mentor.university = data.get("university", mentor.university)
    mentor.qualification_level = data.get("qualification_level", mentor.qualification_level)
    mentor.graduation_year = data.get("graduation_year", mentor.graduation_year)
    mentor.personal_statement = data.get("personal_statement", mentor.personal_statement)
    mentor.expertise = data.get("expertise", mentor.expertise)
    mentor.bio = data.get("bio", mentor.bio)

    db.session.commit()

    return jsonify({"message": "Mentor profile details updated successfully"}), 200


@app.route("/mentors/<int:mentor_id>/credentials", methods=["POST"])
@require_auth
@require_role("mentor")
def add_mentor_credential(mentor_id):
    mentor = MentorProfile.query.get(mentor_id)

    if not mentor:
        return jsonify({"message": "Mentor profile not found"}), 404

    if mentor.user_id != request.current_user.id:
        return jsonify({"message": "You can only edit your own mentor profile"}), 403

    data = get_json_body()
    missing = require_fields(data, ["type", "name"])
    if missing:
        return jsonify({"message": f"Missing required fields: {', '.join(missing)}"}), 400

    if data["type"] not in ("qualification", "certification"):
        return jsonify({"message": "type must be 'qualification' or 'certification'"}), 400

    credential = MentorCredential(
        mentor_id=mentor_id,
        type=data["type"],
        name=data["name"],
        institution=data.get("institution"),
        year=data.get("year")
    )
    db.session.add(credential)
    db.session.commit()

    return jsonify({
        "message": "Credential added successfully",
        "credential": {
            "id": credential.id,
            "type": credential.type,
            "name": credential.name,
            "institution": credential.institution,
            "year": credential.year
        }
    }), 201


@app.route("/mentors/<int:mentor_id>/credentials", methods=["GET"])
def get_mentor_credentials(mentor_id):
    credentials = MentorCredential.query.filter_by(mentor_id=mentor_id).all()

    result = [{
        "id": c.id,
        "type": c.type,
        "name": c.name,
        "institution": c.institution,
        "year": c.year
    } for c in credentials]

    return jsonify(result)


@app.route("/mentor-credentials/<int:credential_id>", methods=["DELETE"])
@require_auth
@require_role("mentor")
def delete_mentor_credential(credential_id):
    credential = MentorCredential.query.get(credential_id)

    if not credential:
        return jsonify({"message": "Credential not found"}), 404

    mentor = MentorProfile.query.get(credential.mentor_id)
    if not mentor or mentor.user_id != request.current_user.id:
        return jsonify({"message": "You can only edit your own mentor profile"}), 403

    db.session.delete(credential)
    db.session.commit()

    return jsonify({"message": "Credential deleted successfully"}), 200


@app.route("/mentors/<int:mentor_id>/skills", methods=["POST"])
@require_auth
@require_role("mentor")
def add_mentor_skill(mentor_id):
    mentor = MentorProfile.query.get(mentor_id)

    if not mentor:
        return jsonify({"message": "Mentor profile not found"}), 404

    if mentor.user_id != request.current_user.id:
        return jsonify({"message": "You can only edit your own mentor profile"}), 403

    data = get_json_body()
    missing = require_fields(data, ["name"])
    if missing:
        return jsonify({"message": f"Missing required fields: {', '.join(missing)}"}), 400

    skill = MentorSkill(mentor_id=mentor_id, name=data["name"])
    db.session.add(skill)
    db.session.commit()

    return jsonify({
        "message": "Skill added successfully",
        "skill": {"id": skill.id, "name": skill.name}
    }), 201


@app.route("/mentors/<int:mentor_id>/skills", methods=["GET"])
def get_mentor_skills(mentor_id):
    skills = MentorSkill.query.filter_by(mentor_id=mentor_id).all()
    result = [{"id": s.id, "name": s.name} for s in skills]
    return jsonify(result)


@app.route("/mentor-skills/<int:skill_id>", methods=["DELETE"])
@require_auth
@require_role("mentor")
def delete_mentor_skill(skill_id):
    skill = MentorSkill.query.get(skill_id)

    if not skill:
        return jsonify({"message": "Skill not found"}), 404

    mentor = MentorProfile.query.get(skill.mentor_id)
    if not mentor or mentor.user_id != request.current_user.id:
        return jsonify({"message": "You can only edit your own mentor profile"}), 403

    db.session.delete(skill)
    db.session.commit()

    return jsonify({"message": "Skill deleted successfully"}), 200


@app.route("/mentors/<int:mentor_id>/jobs", methods=["POST"])
@require_auth
@require_role("mentor")
def add_mentor_job(mentor_id):
    mentor = MentorProfile.query.get(mentor_id)

    if not mentor:
        return jsonify({"message": "Mentor profile not found"}), 404

    if mentor.user_id != request.current_user.id:
        return jsonify({"message": "You can only edit your own mentor profile"}), 403

    existing_count = MentorJobHistory.query.filter_by(mentor_id=mentor_id).count()
    if existing_count >= 3:
        return jsonify({"message": "You can only list up to 3 jobs"}), 400

    data = get_json_body()
    missing = require_fields(data, ["job_title", "employer"])
    if missing:
        return jsonify({"message": f"Missing required fields: {', '.join(missing)}"}), 400

    job = MentorJobHistory(
        mentor_id=mentor_id,
        job_title=data["job_title"],
        employer=data["employer"],
        start_year=data.get("start_year"),
        end_year=data.get("end_year"),
        is_current=bool(data.get("is_current", False))
    )
    db.session.add(job)
    db.session.commit()

    return jsonify({
        "message": "Job added successfully",
        "job": {
            "id": job.id,
            "job_title": job.job_title,
            "employer": job.employer,
            "start_year": job.start_year,
            "end_year": job.end_year,
            "is_current": job.is_current
        }
    }), 201


@app.route("/mentors/<int:mentor_id>/jobs", methods=["GET"])
def get_mentor_jobs(mentor_id):
    jobs = MentorJobHistory.query.filter_by(mentor_id=mentor_id).all()
    result = [{
        "id": j.id,
        "job_title": j.job_title,
        "employer": j.employer,
        "start_year": j.start_year,
        "end_year": j.end_year,
        "is_current": j.is_current
    } for j in jobs]
    return jsonify(result)


@app.route("/mentor-jobs/<int:job_id>", methods=["DELETE"])
@require_auth
@require_role("mentor")
def delete_mentor_job(job_id):
    job = MentorJobHistory.query.get(job_id)

    if not job:
        return jsonify({"message": "Job not found"}), 404

    mentor = MentorProfile.query.get(job.mentor_id)
    if not mentor or mentor.user_id != request.current_user.id:
        return jsonify({"message": "You can only edit your own mentor profile"}), 403

    db.session.delete(job)
    db.session.commit()

    return jsonify({"message": "Job deleted successfully"}), 200


@app.route("/mentors/<int:mentor_id>/full", methods=["GET"])
@require_auth
def get_mentor_full_profile(mentor_id):
    mentor = MentorProfile.query.get(mentor_id)

    if not mentor:
        return jsonify({"message": "Mentor not found"}), 404

    # Day 9 fix: any authenticated user (student, mentor, staff) may view a
    # mentor's full profile. Previously this was restricted to staff or the
    # mentor themselves, which silently 403'd every student "View Profile"
    # click -- this was the actual cause of the reported View Profile defect,
    # not a frontend routing issue.
    mentor_owner = User.query.get(mentor.user_id) if mentor.user_id else None

    credentials = MentorCredential.query.filter_by(mentor_id=mentor_id).all()
    skills = MentorSkill.query.filter_by(mentor_id=mentor_id).all()
    jobs = MentorJobHistory.query.filter_by(mentor_id=mentor_id).all()
    documents = Document.query.filter_by(user_id=mentor.user_id).all()

    return jsonify({
        "mentor": {
            "id": mentor.id,
            "name": mentor.name,
            "expertise": mentor.expertise,
            "bio": mentor.bio,
            "university": mentor.university,
            "qualification_level": mentor.qualification_level,
            "graduation_year": mentor.graduation_year,
            "personal_statement": mentor.personal_statement,
            "interview_scheduled_at": mentor.interview_scheduled_at.isoformat() if mentor.interview_scheduled_at else None,
            "interview_status": mentor.interview_status,
            # Day 9 addition: explicit verification status, needed so the
            # student-facing profile view can show a visible "Verified" badge
            # (RQ3 -- previously the verification workflow existed but its
            # result was never exposed to the student-facing API response).
            "approved": mentor_owner.approved if mentor_owner else False,
            "verified": bool(mentor_owner and mentor_owner.approved and mentor.interview_status == "Completed")
        },
        "credentials": [{
            "id": c.id, "type": c.type, "name": c.name, "institution": c.institution, "year": c.year
        } for c in credentials],
        "skills": [{"id": s.id, "name": s.name} for s in skills],
        "jobs": [{
            "id": j.id, "job_title": j.job_title, "employer": j.employer,
            "start_year": j.start_year, "end_year": j.end_year, "is_current": j.is_current
        } for j in jobs],
        "documents": [{
            "id": d.id, "original_filename": d.original_filename, "uploaded_at": d.uploaded_at.isoformat()
        } for d in documents]
    })


@app.route("/mentors", methods=["GET"])
def get_mentors():
    # Day 9 fix: only list mentors whose account has been approved, so
    # students never see pending/unapproved mentors in the directory
    # (previously this returned every MentorProfile regardless of approval
    # status).
    mentors = (
        MentorProfile.query
        .join(User, User.id == MentorProfile.user_id)
        .filter(User.approved.is_(True))
        .all()
    )

    result = [{
        "id": m.id,
        "name": m.name,
        "expertise": m.expertise,
        "bio": m.bio,
        "verified": bool(m.interview_status == "Completed")
    } for m in mentors]

    return jsonify(result)


def get_or_create_student_profile(user_id):
    profile = StudentProfile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = StudentProfile(user_id=user_id)
        db.session.add(profile)
        db.session.commit()
    return profile


@app.route("/students/me/profile", methods=["GET"])
@require_auth
@require_role("student")
def get_my_student_profile():
    profile = get_or_create_student_profile(request.current_user.id)
    skills = StudentSkill.query.filter_by(student_id=profile.id).all()
    interests = StudentInterest.query.filter_by(student_id=profile.id).all()

    return jsonify({
        "id": profile.id,
        "name": request.current_user.name,
        "university": profile.university,
        "course": profile.course,
        "year_of_study": profile.year_of_study,
        "bio": profile.bio,
        "skills": [{"id": s.id, "name": s.name} for s in skills],
        "interests": [{"id": i.id, "name": i.name} for i in interests],
    })


@app.route("/students/me/profile", methods=["PUT"])
@require_auth
@require_role("student")
def update_my_student_profile():
    profile = get_or_create_student_profile(request.current_user.id)
    data = get_json_body()

    profile.university = data.get("university", profile.university)
    profile.course = data.get("course", profile.course)
    profile.year_of_study = data.get("year_of_study", profile.year_of_study)
    profile.bio = data.get("bio", profile.bio)

    db.session.commit()

    return jsonify({"message": "Profile updated successfully"}), 200


@app.route("/students/me/skills", methods=["POST"])
@require_auth
@require_role("student")
def add_student_skill():
    profile = get_or_create_student_profile(request.current_user.id)
    data = get_json_body()
    missing = require_fields(data, ["name"])
    if missing:
        return jsonify({"message": f"Missing required fields: {', '.join(missing)}"}), 400

    skill = StudentSkill(student_id=profile.id, name=data["name"])
    db.session.add(skill)
    db.session.commit()

    return jsonify({
        "message": "Skill added successfully",
        "skill": {"id": skill.id, "name": skill.name}
    }), 201


@app.route("/student-skills/<int:skill_id>", methods=["DELETE"])
@require_auth
@require_role("student")
def delete_student_skill(skill_id):
    skill = StudentSkill.query.get(skill_id)
    if not skill:
        return jsonify({"message": "Skill not found"}), 404

    profile = StudentProfile.query.get(skill.student_id)
    if not profile or profile.user_id != request.current_user.id:
        return jsonify({"message": "You can only edit your own profile"}), 403

    db.session.delete(skill)
    db.session.commit()
    return jsonify({"message": "Skill deleted successfully"}), 200


@app.route("/students/me/interests", methods=["POST"])
@require_auth
@require_role("student")
def add_student_interest():
    profile = get_or_create_student_profile(request.current_user.id)
    data = get_json_body()
    missing = require_fields(data, ["name"])
    if missing:
        return jsonify({"message": f"Missing required fields: {', '.join(missing)}"}), 400

    interest = StudentInterest(student_id=profile.id, name=data["name"])
    db.session.add(interest)
    db.session.commit()

    return jsonify({
        "message": "Interest added successfully",
        "interest": {"id": interest.id, "name": interest.name}
    }), 201


@app.route("/student-interests/<int:interest_id>", methods=["DELETE"])
@require_auth
@require_role("student")
def delete_student_interest(interest_id):
    interest = StudentInterest.query.get(interest_id)
    if not interest:
        return jsonify({"message": "Interest not found"}), 404

    profile = StudentProfile.query.get(interest.student_id)
    if not profile or profile.user_id != request.current_user.id:
        return jsonify({"message": "You can only edit your own profile"}), 403

    db.session.delete(interest)
    db.session.commit()
    return jsonify({"message": "Interest deleted successfully"}), 200


@app.route("/feedback-requests", methods=["POST"])
@require_auth
@require_role("student")
def create_feedback_request():
    data = get_json_body()
    missing = require_fields(data, ["title", "description", "mentor_id"])

    if missing:
        return jsonify({"message": f"Missing required fields: {', '.join(missing)}"}), 400

    mentor = MentorProfile.query.get(data["mentor_id"])
    if not mentor:
        return jsonify({"message": "mentor_id does not match any mentor"}), 400

    new_request = FeedbackRequest(
        student_name=request.current_user.name,
        student_id=request.current_user.id,
        title=data["title"],
        description=data["description"],
        mentor_id=data["mentor_id"],
        status="Pending"
    )

    db.session.add(new_request)
    db.session.commit()

    return jsonify({
        "message": "Feedback request created successfully",
        "request": {
            "id": new_request.id,
            "student_name": new_request.student_name,
            "title": new_request.title,
            "description": new_request.description,
            "mentor_id": new_request.mentor_id,
            "status": new_request.status
        }
    }), 201


@app.route("/feedback-requests", methods=["GET"])
@require_auth
def get_feedback_requests():
    user = request.current_user

    if user.role == "student":
        requests_ = FeedbackRequest.query.filter_by(student_id=user.id).all()
    elif user.role == "mentor":
        mentor = MentorProfile.query.filter_by(user_id=user.id).first()
        requests_ = FeedbackRequest.query.filter_by(mentor_id=mentor.id).all() if mentor else []
    else:
        requests_ = FeedbackRequest.query.all()

    result = []
    for req in requests_:
        mentor = MentorProfile.query.get(req.mentor_id)
        result.append({
            "id": req.id,
            "student_name": req.student_name,
            "title": req.title,
            "description": req.description,
            "status": req.status,
            "mentor_id": req.mentor_id,
            "mentor_name": mentor.name if mentor else None
        })

    return jsonify(result)


@app.route("/mentor-dashboard/<int:mentor_id>", methods=["GET"])
@require_auth
@require_role("mentor")
def mentor_dashboard(mentor_id):
    if not request.current_user.approved:
        return jsonify({"message": "Your mentor account is pending approval"}), 403

    mentor = MentorProfile.query.get(mentor_id)

    if not mentor:
        return jsonify({"message": "Mentor not found"}), 404

    if mentor.user_id != request.current_user.id:
        return jsonify({"message": "You can only view your own dashboard"}), 403

    assigned_requests = FeedbackRequest.query.filter_by(mentor_id=mentor_id).all()

    result = [{
        "id": r.id,
        "student_name": r.student_name,
        "title": r.title,
        "description": r.description,
        "status": r.status
    } for r in assigned_requests]

    return jsonify({
        "mentor": {
            "id": mentor.id,
            "name": mentor.name,
            "expertise": mentor.expertise
        },
        "assigned_requests": result
    })


@app.route("/feedback-requests/<int:request_id>", methods=["GET"])
def get_request_details(request_id):
    feedback_request = FeedbackRequest.query.get(request_id)

    if not feedback_request:
        return jsonify({"message": "Feedback request not found"}), 404

    mentor = MentorProfile.query.get(feedback_request.mentor_id)
    comments = FeedbackComment.query.filter_by(request_id=request_id).all()

    comment_list = []
    for comment in comments:
        comment_mentor = MentorProfile.query.get(comment.mentor_id)
        comment_list.append({
            "id": comment.id,
            "mentor_id": comment.mentor_id,
            "mentor_name": comment_mentor.name if comment_mentor else None,
            "comment": comment.comment
        })

    return jsonify({
        "request": {
            "id": feedback_request.id,
            "student_name": feedback_request.student_name,
            "title": feedback_request.title,
            "description": feedback_request.description,
            "status": feedback_request.status,
            "mentor_id": feedback_request.mentor_id,
            "mentor_name": mentor.name if mentor else None
        },
        "comments": comment_list
    })


@app.route("/feedback-comments", methods=["POST"])
@require_auth
@require_role("mentor")
def add_feedback_comment():
    data = get_json_body()
    missing = require_fields(data, ["request_id", "comment"])

    if missing:
        return jsonify({"message": f"Missing required fields: {', '.join(missing)}"}), 400

    feedback_request = FeedbackRequest.query.get(data["request_id"])
    if not feedback_request:
        return jsonify({"message": "Feedback request not found"}), 404

    mentor = MentorProfile.query.filter_by(user_id=request.current_user.id).first()
    if not mentor:
        return jsonify({"message": "No mentor profile found for this account"}), 400

    if feedback_request.mentor_id != mentor.id:
        return jsonify({"message": "You can only comment on requests assigned to you"}), 403

    new_comment = FeedbackComment(
        request_id=data["request_id"],
        mentor_id=mentor.id,
        comment=data["comment"]
    )

    db.session.add(new_comment)
    db.session.commit()

    return jsonify({
        "message": "Feedback comment added successfully",
        "comment": {
            "id": new_comment.id,
            "request_id": new_comment.request_id,
            "mentor_id": new_comment.mentor_id,
            "mentor_name": mentor.name,
            "comment": new_comment.comment
        }
    }), 201


@app.route("/feedback-comments/<int:request_id>", methods=["GET"])
def get_feedback_comments(request_id):
    comments = FeedbackComment.query.filter_by(request_id=request_id).all()

    result = []
    for comment in comments:
        mentor = MentorProfile.query.get(comment.mentor_id)
        result.append({
            "id": comment.id,
            "request_id": comment.request_id,
            "mentor_id": comment.mentor_id,
            "mentor_name": mentor.name if mentor else None,
            "comment": comment.comment
        })

    return jsonify(result)


@app.route("/feedback-requests/<int:request_id>/status", methods=["PUT"])
@require_auth
@require_role("mentor", "manager")
def update_request_status(request_id):
    feedback_request = FeedbackRequest.query.get(request_id)

    if not feedback_request:
        return jsonify({"message": "Feedback request not found"}), 404

    user = request.current_user

    if user.role == "mentor":
        mentor = MentorProfile.query.filter_by(user_id=user.id).first()
        if not mentor or feedback_request.mentor_id != mentor.id:
            return jsonify({"message": "You can only update requests assigned to you"}), 403

    data = get_json_body()
    new_status = data.get("status")

    if new_status not in VALID_STATUSES:
        return jsonify({"message": f"status must be one of {VALID_STATUSES}"}), 400

    current_status = feedback_request.status

    if user.role == "mentor" and new_status != current_status and new_status not in ALLOWED_TRANSITIONS.get(current_status, []):
        return jsonify({
            "message": f"Cannot move status from '{current_status}' to '{new_status}'",
            "allowed_next_statuses": ALLOWED_TRANSITIONS.get(current_status, [])
        }), 400

    feedback_request.status = new_status
    db.session.commit()

    return jsonify({
        "message": "Request status updated successfully",
        "request": {
            "id": feedback_request.id,
            "title": feedback_request.title,
            "status": feedback_request.status
        }
    })


@app.route("/feedback-requests/<int:request_id>", methods=["DELETE"])
@require_auth
@require_role("manager")
def delete_feedback_request(request_id):
    feedback_request = FeedbackRequest.query.get(request_id)

    if not feedback_request:
        return jsonify({"message": "Feedback request not found"}), 404

    FeedbackComment.query.filter_by(request_id=request_id).delete()
    db.session.delete(feedback_request)
    db.session.commit()

    return jsonify({"message": "Feedback request deleted successfully"}), 200


@app.route("/feedback-comments/<int:comment_id>", methods=["PUT"])
@require_auth
@require_role("manager")
def update_feedback_comment(comment_id):
    comment = FeedbackComment.query.get(comment_id)

    if not comment:
        return jsonify({"message": "Feedback comment not found"}), 404

    data = get_json_body()
    missing = require_fields(data, ["comment"])
    if missing:
        return jsonify({"message": f"Missing required fields: {', '.join(missing)}"}), 400

    comment.comment = data["comment"]
    db.session.commit()

    return jsonify({"message": "Feedback comment updated successfully"}), 200


@app.route("/feedback-comments/<int:comment_id>", methods=["DELETE"])
@require_auth
@require_role("manager")
def delete_feedback_comment(comment_id):
    comment = FeedbackComment.query.get(comment_id)

    if not comment:
        return jsonify({"message": "Feedback comment not found"}), 404

    db.session.delete(comment)
    db.session.commit()

    return jsonify({"message": "Feedback comment deleted successfully"}), 200


@app.route("/documents", methods=["POST"])
@require_auth
def upload_document():
    if "file" not in request.files:
        return jsonify({"message": "No file provided"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"message": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"message": "File type not allowed. Use PDF, DOC, DOCX, PNG or JPG."}), 400

    original_filename = file.filename
    safe_name = secure_filename(original_filename)
    stored_name = f"{request.current_user.id}_{secrets.token_hex(8)}_{safe_name}"
    file.save(os.path.join(app.config["UPLOAD_FOLDER"], stored_name))

    new_document = Document(
        user_id=request.current_user.id,
        filename=stored_name,
        original_filename=original_filename
    )
    db.session.add(new_document)
    db.session.commit()

    return jsonify({
        "message": "Document uploaded successfully",
        "document": {
            "id": new_document.id,
            "original_filename": new_document.original_filename,
            "uploaded_at": new_document.uploaded_at.isoformat()
        }
    }), 201


@app.route("/documents/me", methods=["GET"])
@require_auth
def get_my_documents():
    documents = Document.query.filter_by(user_id=request.current_user.id).all()

    result = [{
        "id": d.id,
        "original_filename": d.original_filename,
        "uploaded_at": d.uploaded_at.isoformat()
    } for d in documents]

    return jsonify(result)


@app.route("/documents/user/<int:user_id>", methods=["GET"])
@require_auth
@require_role("manager")
def get_user_documents(user_id):
    documents = Document.query.filter_by(user_id=user_id).all()

    result = [{
        "id": d.id,
        "original_filename": d.original_filename,
        "uploaded_at": d.uploaded_at.isoformat()
    } for d in documents]

    return jsonify(result)


@app.route("/documents/<int:document_id>/download", methods=["GET"])
def download_document(document_id):
    auth_header = request.headers.get("Authorization", "")
    token_value = auth_header.split(" ", 1)[1] if auth_header.startswith("Bearer ") else request.args.get("token", "")

    token_row = AuthToken.query.filter_by(token=token_value).first()
    if not token_row or token_row.expires_at < datetime.utcnow():
        return jsonify({"message": "Invalid or expired token"}), 401

    current_user = User.query.get(token_row.user_id)
    if not current_user:
        return jsonify({"message": "User account no longer exists"}), 401

    document = Document.query.get(document_id)
    if not document:
        return jsonify({"message": "Document not found"}), 404

    if document.user_id != current_user.id and current_user.role != "manager":
        return jsonify({"message": "You do not have access to this document"}), 403

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        document.filename,
        as_attachment=True,
        download_name=document.original_filename
    )


@app.route("/documents/<int:document_id>", methods=["DELETE"])
@require_auth
def delete_document(document_id):
    document = Document.query.get(document_id)

    if not document:
        return jsonify({"message": "Document not found"}), 404

    if document.user_id != request.current_user.id and request.current_user.role != "manager":
        return jsonify({"message": "You do not have access to this document"}), 403

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], document.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(document)
    db.session.commit()

    return jsonify({"message": "Document deleted successfully"}), 200


@app.route("/users/pending", methods=["GET"])
@require_auth
@require_role("manager")
def get_pending_users():
    # Day 10 fix: previously this only looked at approved=False, so a
    # mentor who was already marked approved (e.g. via old test data or a
    # manual DB edit) but never had their interview completed became
    # permanently invisible here -- the manager had no way to schedule or
    # complete that interview. Now it shows anyone not yet "fully onboarded":
    # not approved, OR approved but interview not completed.
    pending = User.query.filter_by(role="mentor").join(
        MentorProfile, MentorProfile.user_id == User.id
    ).filter(
        (User.approved.is_(False)) | (MentorProfile.interview_status != "Completed")
    ).all()

    result = []
    for u in pending:
        mentor = MentorProfile.query.filter_by(user_id=u.id).first()
        docs = Document.query.filter_by(user_id=u.id).all()
        result.append({
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "mentor_id": mentor.id if mentor else None,
            "interview_status": mentor.interview_status if mentor else None,
            "interview_scheduled_at": mentor.interview_scheduled_at.isoformat() if mentor and mentor.interview_scheduled_at else None,
            "documents": [{
                "id": d.id,
                "original_filename": d.original_filename,
                "uploaded_at": d.uploaded_at.isoformat()
            } for d in docs]
        })

    return jsonify(result)


@app.route("/users/<int:user_id>/interview", methods=["PUT"])
@require_auth
@require_role("manager")
def schedule_interview(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    mentor = MentorProfile.query.filter_by(user_id=user.id).first()
    if not mentor:
        return jsonify({"message": "This user has no mentor profile"}), 400

    data = get_json_body()
    missing = require_fields(data, ["scheduled_at"])
    if missing:
        return jsonify({"message": f"Missing required fields: {', '.join(missing)}"}), 400

    try:
        scheduled_at = datetime.fromisoformat(data["scheduled_at"])
    except ValueError:
        return jsonify({"message": "scheduled_at must be a valid ISO datetime string"}), 400

    mentor.interview_scheduled_at = scheduled_at
    mentor.interview_status = "Scheduled"
    db.session.commit()

    return jsonify({"message": "Interview scheduled successfully"}), 200


@app.route("/users/<int:user_id>/interview/complete", methods=["PUT"])
@require_auth
@require_role("manager")
def complete_interview(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    mentor = MentorProfile.query.filter_by(user_id=user.id).first()
    if not mentor:
        return jsonify({"message": "This user has no mentor profile"}), 400

    mentor.interview_status = "Completed"
    db.session.commit()

    return jsonify({"message": "Interview marked as completed"}), 200


@app.route("/users/<int:user_id>/approve", methods=["PUT"])
@require_auth
@require_role("manager")
def approve_user(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    if user.role == "mentor":
        mentor = MentorProfile.query.filter_by(user_id=user.id).first()
        if not mentor or mentor.interview_status != "Completed":
            return jsonify({"message": "Interview must be completed before this mentor can be approved"}), 400

    user.approved = True
    db.session.commit()

    return jsonify({"message": "User approved successfully"}), 200


@app.route("/users/<int:user_id>/reject", methods=["DELETE"])
@require_auth
@require_role("manager")
def reject_user(user_id):
    user = User.query.get(user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    mentor = MentorProfile.query.filter_by(user_id=user.id).first()
    if mentor:
        FeedbackRequest.query.filter_by(mentor_id=mentor.id).delete()
        MentorCredential.query.filter_by(mentor_id=mentor.id).delete()
        MentorSkill.query.filter_by(mentor_id=mentor.id).delete()
        MentorJobHistory.query.filter_by(mentor_id=mentor.id).delete()
        db.session.delete(mentor)

    documents = Document.query.filter_by(user_id=user.id).all()
    for d in documents:
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], d.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        db.session.delete(d)

    AuthToken.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User rejected and removed successfully"}), 200


@app.route("/complaints", methods=["POST"])
@require_auth
@require_role("student", "mentor")
def submit_complaint():
    data = get_json_body()
    missing = require_fields(data, ["subject", "description"])
    if missing:
        return jsonify({"message": f"Missing required fields: {', '.join(missing)}"}), 400

    complaint = Complaint(
        submitted_by_id=request.current_user.id,
        submitted_by_name=request.current_user.name,
        submitted_by_role=request.current_user.role,
        subject=data["subject"],
        description=data["description"],
        status="Open"
    )
    db.session.add(complaint)
    db.session.commit()

    return jsonify({"message": "Complaint submitted successfully"}), 201


@app.route("/complaints", methods=["GET"])
@require_auth
@require_role("manager", "complaints")
def get_complaints():
    complaints = Complaint.query.order_by(Complaint.created_at.desc()).all()

    result = [{
        "id": c.id,
        "submitted_by_name": c.submitted_by_name,
        "submitted_by_role": c.submitted_by_role,
        "subject": c.subject,
        "description": c.description,
        "status": c.status,
        "created_at": c.created_at.isoformat()
    } for c in complaints]

    return jsonify(result)


@app.route("/complaints/<int:complaint_id>/status", methods=["PUT"])
@require_auth
@require_role("manager", "complaints")
def update_complaint_status(complaint_id):
    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        return jsonify({"message": "Complaint not found"}), 404

    data = get_json_body()
    new_status = data.get("status")
    if new_status not in ("Open", "Resolved"):
        return jsonify({"message": "status must be 'Open' or 'Resolved'"}), 400

    complaint.status = new_status
    db.session.commit()

    return jsonify({"message": "Complaint status updated successfully"}), 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)