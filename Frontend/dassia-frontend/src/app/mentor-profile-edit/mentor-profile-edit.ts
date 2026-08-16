import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService, MentorCredential, MentorSkillItem, MentorJob } from '../services/api';
import { AuthService } from '../services/auth';

@Component({
  selector: 'app-mentor-profile-edit',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './mentor-profile-edit.html',
  styleUrl: './mentor-profile-edit.css',
})
export class MentorProfileEdit implements OnInit {
  mentorId: number | null = null;

  university = '';
  qualificationLevel = '';
  graduationYear: number | null = null;
  personalStatement = '';
  expertise = '';
  bio = '';

  credentials = signal<MentorCredential[]>([]);
  skills = signal<MentorSkillItem[]>([]);
  jobs = signal<MentorJob[]>([]);

  newCredentialType: 'qualification' | 'certification' = 'qualification';
  newCredentialName = '';
  newCredentialInstitution = '';
  newCredentialYear: number | null = null;

  newSkillName = '';

  newJobTitle = '';
  newJobEmployer = '';
  newJobStartYear: number | null = null;
  newJobEndYear: number | null = null;
  newJobIsCurrent = false;

  isSavingBasics = signal(false);
  basicsSaved = signal(false);
  errorMessage = signal<string | null>(null);

  constructor(
    private api: ApiService,
    private auth: AuthService
  ) {}

  ngOnInit(): void {
    this.mentorId = this.auth.currentUser()?.mentor_id ?? null;
    if (!this.mentorId) {
      this.errorMessage.set('This account has no linked mentor profile.');
      return;
    }
    this.loadFullProfile();
  }

  loadFullProfile(): void {
    if (!this.mentorId) return;

    this.api.getMentorFullProfile(this.mentorId).subscribe({
      next: (data) => {
        this.university = data.mentor.university ?? '';
        this.qualificationLevel = data.mentor.qualification_level ?? '';
        this.graduationYear = data.mentor.graduation_year ?? null;
        this.personalStatement = data.mentor.personal_statement ?? '';
        this.expertise = data.mentor.expertise ?? '';
        this.bio = data.mentor.bio ?? '';
        this.credentials.set(data.credentials);
        this.skills.set(data.skills);
        this.jobs.set(data.jobs);
      },
      error: () => this.errorMessage.set('Could not load your profile.'),
    });
  }

  saveBasics(): void {
    if (!this.mentorId) return;

    this.isSavingBasics.set(true);
    this.basicsSaved.set(false);

    this.api.updateMentorProfileDetails(this.mentorId, {
      university: this.university,
      qualification_level: this.qualificationLevel,
      graduation_year: this.graduationYear ?? undefined,
      personal_statement: this.personalStatement,
      expertise: this.expertise,
      bio: this.bio,
    }).subscribe({
      next: () => {
        this.isSavingBasics.set(false);
        this.basicsSaved.set(true);
      },
      error: () => {
        this.isSavingBasics.set(false);
        this.errorMessage.set('Could not save your profile.');
      },
    });
  }

  addCredential(): void {
    if (!this.mentorId || !this.newCredentialName.trim()) return;

    this.api.addMentorCredential(this.mentorId, {
      type: this.newCredentialType,
      name: this.newCredentialName.trim(),
      institution: this.newCredentialInstitution.trim() || undefined,
      year: this.newCredentialYear ?? undefined,
    }).subscribe({
      next: () => {
        this.newCredentialName = '';
        this.newCredentialInstitution = '';
        this.newCredentialYear = null;
        this.loadFullProfile();
      },
      error: () => this.errorMessage.set('Could not add credential.'),
    });
  }

  deleteCredential(id: number): void {
    if (!confirm('Delete this qualification or certification? This cannot be undone.')) {
      return;
    }

    this.api.deleteMentorCredential(id).subscribe({
      next: () => this.loadFullProfile(),
      error: () => this.errorMessage.set('Could not delete credential.'),
    });
  }

  addSkill(): void {
    if (!this.mentorId || !this.newSkillName.trim()) return;

    this.api.addMentorSkill(this.mentorId, this.newSkillName.trim()).subscribe({
      next: () => {
        this.newSkillName = '';
        this.loadFullProfile();
      },
      error: () => this.errorMessage.set('Could not add skill.'),
    });
  }

  deleteSkill(id: number): void {
    if (!confirm('Remove this skill from your profile?')) {
      return;
    }

    this.api.deleteMentorSkill(id).subscribe({
      next: () => this.loadFullProfile(),
      error: () => this.errorMessage.set('Could not delete skill.'),
    });
  }

  addJob(): void {
    if (!this.mentorId || !this.newJobTitle.trim() || !this.newJobEmployer.trim()) return;

    if (this.jobs().length >= 3) {
      this.errorMessage.set('You can only list up to 3 jobs.');
      return;
    }

    this.api.addMentorJob(this.mentorId, {
      job_title: this.newJobTitle.trim(),
      employer: this.newJobEmployer.trim(),
      start_year: this.newJobStartYear ?? undefined,
      end_year: this.newJobIsCurrent ? undefined : (this.newJobEndYear ?? undefined),
      is_current: this.newJobIsCurrent,
    }).subscribe({
      next: () => {
        this.newJobTitle = '';
        this.newJobEmployer = '';
        this.newJobStartYear = null;
        this.newJobEndYear = null;
        this.newJobIsCurrent = false;
        this.loadFullProfile();
      },
      error: (err) => {
        this.errorMessage.set(
          err.status === 400 ? 'You can only list up to 3 jobs.' : 'Could not add job.'
        );
      },
    });
  }

  deleteJob(id: number): void {
    if (!confirm('Delete this work history entry? This cannot be undone.')) {
      return;
    }

    this.api.deleteMentorJob(id).subscribe({
      next: () => this.loadFullProfile(),
      error: () => this.errorMessage.set('Could not delete job.'),
    });
  }
}