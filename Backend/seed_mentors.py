from app import app, db, User, MentorProfile, MentorCredential, MentorSkill, MentorJobHistory
from werkzeug.security import generate_password_hash


def make_email(full_name: str) -> str:
    # "Dr Esme Tune" -> "esme.tune@dassianexus.ac.uk"
    parts = full_name.replace("Dr ", "").replace("Dr. ", "").strip().split(" ")
    return f"{parts[0].lower()}.{parts[-1].lower()}@dassianexus.ac.uk"


def make_password(full_name: str) -> str:
    # "Dr Esme Tune" -> "EsmeTune2026!"
    parts = full_name.replace("Dr ", "").replace("Dr. ", "").strip().split(" ")
    return f"{parts[0]}{parts[-1]}2026!"


MENTORS = [
    {
        "name": "Dr Esme Tune",
        "university": "University of Manchester",
        "qualification_level": "PhD in Business and Management",
        "graduation_year": 2015,
        "expertise": "Digital Transformation & Leadership",
        "credentials": [
            ("qualification", "PhD in Business and Management", "University of Manchester", 2015),
            ("qualification", "MSc in Strategic Management", "University of Manchester", None),
            ("qualification", "BSc (Hons) Business Management", "University of Manchester", None),
        ],
        "skills": ["Digital Transformation", "Leadership", "Change Management", "Strategic Management",
                    "Project Management", "Business Analysis", "Research Methods"],
        "jobs": [
            ("Senior Lecturer in Digital Transformation and Leadership", "University of Manchester", 2022, None, True),
            ("Lecturer in Business and Management", "University of Manchester", 2018, 2022, False),
            ("Digital Transformation Consultant", "Industry", 2015, 2018, False),
        ],
    },
    {
        "name": "Dr Sarah Ahmed",
        "university": "University of Birmingham",
        "qualification_level": "PhD in Computer Science",
        "graduation_year": 2015,
        "expertise": "Machine Learning & Artificial Intelligence",
        "credentials": [
            ("qualification", "PhD in Computer Science", "University of Birmingham", 2015),
            ("qualification", "MSc in Artificial Intelligence", "University of Birmingham", None),
            ("qualification", "BSc (Hons) Computer Science", "University of Birmingham", None),
        ],
        "skills": ["Machine Learning", "Artificial Intelligence", "Deep Learning", "Python",
                    "Data Science", "Data Analysis", "Research Methods"],
        "jobs": [
            ("Senior Lecturer in Machine Learning", "University of Birmingham", 2022, None, True),
            ("Lecturer in Computer Science", "University of Birmingham", 2018, 2022, False),
            ("Machine Learning Research Associate", "Industry", 2015, 2018, False),
        ],
    },
    {
        "name": "Dr James Walker",
        "university": "University of Leeds",
        "qualification_level": "PhD in Cyber Security",
        "graduation_year": 2015,
        "expertise": "Cyber Security & Network Security",
        "credentials": [
            ("qualification", "PhD in Cyber Security", "University of Leeds", 2015),
            ("qualification", "MSc Information Security", "University of Leeds", None),
            ("qualification", "BSc (Hons) Computer Science", "University of Leeds", None),
        ],
        "skills": ["Cyber Security", "Network Security", "Ethical Hacking", "Risk Management",
                    "Penetration Testing", "Information Assurance", "Research Methods"],
        "jobs": [
            ("Senior Lecturer in Cyber Security", "University of Leeds", 2022, None, True),
            ("Lecturer in Information Security", "University of Leeds", 2018, 2022, False),
            ("Cyber Security Consultant", "Industry", 2015, 2018, False),
        ],
    },
    {
        "name": "Dr Emily Carter",
        "university": "University of Nottingham",
        "qualification_level": "PhD in Data Science",
        "graduation_year": 2015,
        "expertise": "Data Science & Analytics",
        "credentials": [
            ("qualification", "PhD in Data Science", "University of Nottingham", 2015),
            ("qualification", "MSc Data Analytics", "University of Nottingham", None),
            ("qualification", "BSc (Hons) Mathematics", "University of Nottingham", None),
        ],
        "skills": ["Data Science", "Data Analytics", "Python", "SQL",
                    "Statistical Analysis", "Data Visualisation", "Research Methods"],
        "jobs": [
            ("Senior Lecturer in Data Science", "University of Nottingham", 2022, None, True),
            ("Lecturer in Data Analytics", "University of Nottingham", 2018, 2022, False),
            ("Data Scientist", "Industry", 2015, 2018, False),
        ],
    },
    {
        "name": "Dr Michael Evans",
        "university": "University of Southampton",
        "qualification_level": "PhD in Software Engineering",
        "graduation_year": 2015,
        "expertise": "Software Engineering & Architecture",
        "credentials": [
            ("qualification", "PhD in Software Engineering", "University of Southampton", 2015),
            ("qualification", "MSc Software Development", "University of Southampton", None),
            ("qualification", "BSc (Hons) Computer Science", "University of Southampton", None),
        ],
        "skills": ["Software Engineering", "Software Architecture", "Agile Development", "Java",
                    "C#", "System Design", "Research Methods"],
        "jobs": [
            ("Senior Lecturer in Software Engineering", "University of Southampton", 2022, None, True),
            ("Lecturer in Computer Science", "University of Southampton", 2018, 2022, False),
            ("Software Engineer", "Industry", 2015, 2018, False),
        ],
    },
    {
        "name": "Dr Olivia Brown",
        "university": "University of Warwick",
        "qualification_level": "PhD in Business Analytics",
        "graduation_year": 2015,
        "expertise": "Business Analytics & Intelligence",
        "credentials": [
            ("qualification", "PhD in Business Analytics", "University of Warwick", 2015),
            ("qualification", "MSc Business Analytics", "University of Warwick", None),
            ("qualification", "BSc (Hons) Business Management", "University of Warwick", None),
        ],
        "skills": ["Business Analytics", "Business Intelligence", "Data-Driven Decision Making",
                    "Process Improvement", "Statistics", "Tableau", "Research Methods"],
        "jobs": [
            ("Senior Lecturer in Business Analytics", "University of Warwick", 2022, None, True),
            ("Lecturer in Business Information Systems", "University of Warwick", 2018, 2022, False),
            ("Business Analyst", "Industry", 2015, 2018, False),
        ],
    },
    {
        "name": "Dr Daniel Foster",
        "university": "University of Bristol",
        "qualification_level": "PhD in Cloud Computing",
        "graduation_year": 2015,
        "expertise": "Cloud Computing & DevOps",
        "credentials": [
            ("qualification", "PhD in Cloud Computing", "University of Bristol", 2015),
            ("qualification", "MSc Cloud Technologies", "University of Bristol", None),
            ("qualification", "BSc (Hons) Computer Science", "University of Bristol", None),
        ],
        "skills": ["Cloud Computing", "AWS", "Microsoft Azure", "DevOps",
                    "Docker", "Kubernetes", "Research Methods"],
        "jobs": [
            ("Senior Lecturer in Cloud Computing", "University of Bristol", 2022, None, True),
            ("Lecturer in Distributed Systems", "University of Bristol", 2018, 2022, False),
            ("Cloud Solutions Architect", "Industry", 2015, 2018, False),
        ],
    },
    {
        "name": "Dr Sophie Green",
        "university": "King's College London",
        "qualification_level": "PhD in Health and Social Care",
        "graduation_year": 2015,
        "expertise": "Health and Social Care & Public Health",
        "credentials": [
            ("qualification", "PhD in Health and Social Care", "King's College London", 2015),
            ("qualification", "MSc Public Health", "King's College London", None),
            ("qualification", "BSc (Hons) Health and Social Care", "King's College London", None),
        ],
        "skills": ["Health and Social Care", "Public Health", "Health Policy", "Patient-Centred Care",
                    "Healthcare Management", "Research Methods", "Evidence-Based Practice"],
        "jobs": [
            ("Senior Lecturer in Health and Social Care", "King's College London", 2022, None, True),
            ("Lecturer in Public Health", "King's College London", 2018, 2022, False),
            ("Health Services Researcher", "Industry", 2015, 2018, False),
        ],
    },
    {
        "name": "Dr Rebecca Wilson",
        "university": "University of Sheffield",
        "qualification_level": "PhD in Nursing",
        "graduation_year": 2015,
        "expertise": "Nursing Practice & Clinical Leadership",
        "credentials": [
            ("qualification", "PhD in Nursing", "University of Sheffield", 2015),
            ("qualification", "MSc Advanced Nursing Practice", "University of Sheffield", None),
            ("qualification", "BSc (Hons) Adult Nursing", "University of Sheffield", None),
            ("certification", "Registered Nurse (NMC)", "Nursing and Midwifery Council", None),
        ],
        "skills": ["Nursing Practice", "Clinical Leadership", "Patient Care", "Evidence-Based Practice",
                    "Clinical Education", "Healthcare Research", "Research Methods"],
        "jobs": [
            ("Senior Lecturer in Nursing", "University of Sheffield", 2022, None, True),
            ("Lecturer in Adult Nursing", "University of Sheffield", 2018, 2022, False),
            ("Clinical Nurse Specialist", "Industry", 2015, 2018, False),
        ],
    },
    {
        "name": "Dr Thomas Hughes",
        "university": "Loughborough University",
        "qualification_level": "PhD in Construction Management",
        "graduation_year": 2015,
        "expertise": "Construction Management & BIM",
        "credentials": [
            ("qualification", "PhD in Construction Management", "Loughborough University", 2015),
            ("qualification", "MSc Construction Project Management", "Loughborough University", None),
            ("qualification", "BSc (Hons) Construction Management", "Loughborough University", None),
        ],
        "skills": ["Construction Management", "Building Information Modelling (BIM)", "Project Planning",
                    "Health and Safety", "Sustainable Construction", "Risk Management", "Research Methods"],
        "jobs": [
            ("Senior Lecturer in Construction Management", "Loughborough University", 2022, None, True),
            ("Lecturer in Construction Engineering", "Loughborough University", 2018, 2022, False),
            ("Construction Project Manager", "Industry", 2015, 2018, False),
        ],
    },
    {
        "name": "Dr Benjamin Clark",
        "university": "Cranfield University",
        "qualification_level": "PhD in Project Management",
        "graduation_year": 2015,
        "expertise": "Project Management & Agile Delivery",
        "credentials": [
            ("qualification", "PhD in Project Management", "Cranfield University", 2015),
            ("qualification", "MSc Project Management", "Cranfield University", None),
            ("qualification", "BSc (Hons) Business Management", "Cranfield University", None),
            ("certification", "PRINCE2 Practitioner", "AXELOS", None),
            ("certification", "AgilePM Practitioner", "APMG International", None),
        ],
        "skills": ["Project Management", "Agile Project Management", "Risk Management",
                    "Stakeholder Management", "Strategic Planning", "Leadership", "Research Methods"],
        "jobs": [
            ("Senior Lecturer in Project Management", "Cranfield University", 2022, None, True),
            ("Lecturer in Business and Project Management", "Cranfield University", 2018, 2022, False),
            ("Project Manager", "Industry", 2015, 2018, False),
        ],
    },
]


def upsert_mentor(data: dict) -> tuple[str, str, str]:
    email = make_email(data["name"])
    password = make_password(data["name"])

    user = User.query.filter(
        (User.email == email) | (User.name == data["name"])
    ).first()

    if user is None:
        user = User(
            name=data["name"],
            email=email,
            role="mentor",
            password_hash=generate_password_hash(password),
            approved=True,
        )
        db.session.add(user)
        db.session.commit()
        status = "CREATED"
    else:
        user.email = email
        user.password_hash = generate_password_hash(password)
        user.approved = True
        db.session.commit()
        status = "UPDATED"

    profile = MentorProfile.query.filter_by(user_id=user.id).first()
    if profile is None:
        profile = MentorProfile(user_id=user.id, name=data["name"])
        db.session.add(profile)
        db.session.commit()

    profile.name = data["name"]
    profile.expertise = data["expertise"]
    profile.bio = (
        f"{data['name']} is a {data['jobs'][0][0]} at {data['university']}, "
        f"specialising in {data['expertise'].lower()}."
    )
    profile.university = data["university"]
    profile.qualification_level = data["qualification_level"]
    profile.graduation_year = data["graduation_year"]
    profile.personal_statement = (
        f"I hold a {data['qualification_level']} from {data['university']} and bring "
        f"industry and academic experience in {data['expertise'].lower()} to every mentoring session."
    )
    profile.interview_status = "Completed"
    db.session.commit()

    # Reset credentials / skills / jobs so re-running this script never duplicates rows
    MentorCredential.query.filter_by(mentor_id=profile.id).delete()
    MentorSkill.query.filter_by(mentor_id=profile.id).delete()
    MentorJobHistory.query.filter_by(mentor_id=profile.id).delete()
    db.session.commit()

    for c_type, c_name, c_institution, c_year in data["credentials"]:
        db.session.add(MentorCredential(
            mentor_id=profile.id, type=c_type, name=c_name,
            institution=c_institution, year=c_year,
        ))

    for skill_name in data["skills"]:
        db.session.add(MentorSkill(mentor_id=profile.id, name=skill_name))

    for job_title, employer, start_year, end_year, is_current in data["jobs"]:
        db.session.add(MentorJobHistory(
            mentor_id=profile.id, job_title=job_title, employer=employer,
            start_year=start_year, end_year=end_year, is_current=is_current,
        ))

    db.session.commit()

    return data["name"], email, password, status


if __name__ == "__main__":
    with app.app_context():
        results = [upsert_mentor(m) for m in MENTORS]

    print("\n" + "=" * 72)
    print(f"{'Name':<20}{'Email':<32}{'Password':<16}{'Status'}")
    print("=" * 72)
    for name, email, password, status in results:
        print(f"{name:<20}{email:<32}{password:<16}{status}")
    print("=" * 72)
    print(f"\nDone. {len(results)} mentors processed.")