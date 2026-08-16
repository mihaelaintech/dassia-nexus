# Dassia Nexus

A digital academic mentoring platform connecting postgraduate students with
verified academic mentors for structured research feedback.

Developed as the artefact component of an MSc dissertation (COM748), evaluated
as a Design Science Research project.

**Evaluation build:** `EVALUATION_FREEZE_2026-08-01`
No functional changes have been made to the application after this freeze point.

---

## Technology Stack

| Layer | Technology |
| --- | --- |
| Frontend | Angular |
| Backend | Flask (Python) |
| ORM | SQLAlchemy |
| Database | SQLite |

---

## Repository Structure
Dassia/
├── Backend/                    Flask API, models, routes
│   ├── app.py                  Application entry point
│   ├── requirements.txt        Python dependencies
│   └── .env.example            Template for environment variables
└── Frontend/
    └── dassia-frontend/        Angular application
---

## Prerequisites

- Python 3.10 or later
- Node.js 18 or later, with npm
- Angular CLI (`npm install -g @angular/cli`)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/mihaelaintech/dassia-nexus.git
cd dassia-nexus
```

### 2. Backend setup

```bash
cd Backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

Create the environment file by copying the template:

```bash
copy .env.example .env         # Windows
# cp .env.example .env         # macOS / Linux
```

Open `.env` and set a value for `SECRET_KEY`. This file is excluded from
version control and must never be committed.

### 3. Frontend setup

```bash
cd ../Frontend/dassia-frontend
npm install
```

---

## Running the Application

The backend and frontend run as two separate processes, in two terminals.

**Terminal 1 — backend:**

```bash
cd Backend
venv\Scripts\activate
python app.py
```
Runs at `http://localhost:5000`.

> Note: a new terminal window does not inherit an activated virtual
> environment. If registration or login fails with a connection error, confirm
> the venv is active and the backend is running in that session.

**Terminal 2 — frontend:**

```bash
cd Frontend/dassia-frontend
ng serve
```
Runs at `http://localhost:4200`. Open this address in the browser.

---

## Roles

The platform supports four roles, accessed through five entry points
(staff roles share a single sign-in).

| Role | Capabilities |
| --- | --- |
| Student | Register, complete profile, manage skills and interests, browse approved mentors, submit feedback requests |
| Mentor | Register, complete profile, manage credentials/skills/jobs, comment on and progress feedback requests |
| Manager | Approve mentors (schedule and complete interviews), view all feedback requests, view and resolve complaints |
| Complaints | View submitted complaints, mark as resolved, reopen |

Mentors are not visible to students until a manager has completed the
interview and approved the account. Approved mentors display a **Verified**
badge, which confirms that credentials were checked at onboarding.

---

## Test Accounts

Demonstration accounts are seeded for evaluation. All use the password `Demo1234!`.

| Role | Email |
| --- | --- |
| Student | alessia@example.com |
| Mentor | james.walker@dassianexus.ac.uk |
| Manager | manager123@example.com |
| Complaints | complaints123@example.com |

These accounts exist only in the local seeded database and hold no real data.
The application runs locally and is not deployed to any public server.

To exercise the full mentor onboarding pipeline, register a new mentor
account, then sign in as the manager to schedule the interview, mark it
complete, and approve the account. The mentor then appears on the student
browse list marked Verified.

---

## Known Limitations

The following were identified during expert inspection of the frozen build and
are reported as findings rather than patched, in order to preserve
comparability of the evaluation:

- The mentor directory is a flat card grid with no search or filter control.
- Students cannot open a per-request detail view, so the mentor's response is
  not reachable on the student surface.
- Feedback request descriptions render Markdown control characters as literal
  text.
- The Verified badge does not disclose what was verified.

---

## Security

`.env` is excluded from version control via `.gitignore` and must not be
committed. Use `.env.example` as the template. Never commit a real
`SECRET_KEY`.

---

## Author

Mihaela Petre — MSc, QAHE / Ulster University
Supervisor: Dr Edita Gashi---


