import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService, StudentSkillItem, StudentInterestItem } from '../services/api';

@Component({
  selector: 'app-student-profile-edit',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './student-profile-edit.html',
  styleUrl: './student-profile-edit.css',
})
export class StudentProfileEdit implements OnInit {
  university = '';
  course = '';
  yearOfStudy = '';
  bio = '';

  skills = signal<StudentSkillItem[]>([]);
  interests = signal<StudentInterestItem[]>([]);

  newSkillName = '';
  newInterestName = '';

  isSavingBasics = signal(false);
  basicsSaved = signal(false);
  errorMessage = signal<string | null>(null);

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.loadFullProfile();
  }

  loadFullProfile(): void {
    this.api.getMyStudentProfile().subscribe({
      next: (data) => {
        this.university = data.university ?? '';
        this.course = data.course ?? '';
        this.yearOfStudy = data.year_of_study ?? '';
        this.bio = data.bio ?? '';
        this.skills.set(data.skills);
        this.interests.set(data.interests);
      },
      error: () => this.errorMessage.set('Could not load your profile.'),
    });
  }

  saveBasics(): void {
    this.isSavingBasics.set(true);
    this.basicsSaved.set(false);

    this.api.updateMyStudentProfile({
      university: this.university,
      course: this.course,
      year_of_study: this.yearOfStudy,
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

  addSkill(): void {
    if (!this.newSkillName.trim()) return;

    this.api.addStudentSkill(this.newSkillName.trim()).subscribe({
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

    this.api.deleteStudentSkill(id).subscribe({
      next: () => this.loadFullProfile(),
      error: () => this.errorMessage.set('Could not delete skill.'),
    });
  }

  addInterest(): void {
    if (!this.newInterestName.trim()) return;

    this.api.addStudentInterest(this.newInterestName.trim()).subscribe({
      next: () => {
        this.newInterestName = '';
        this.loadFullProfile();
      },
      error: () => this.errorMessage.set('Could not add interest.'),
    });
  }

  deleteInterest(id: number): void {
    if (!confirm('Remove this interest from your profile?')) {
      return;
    }

    this.api.deleteStudentInterest(id).subscribe({
      next: () => this.loadFullProfile(),
      error: () => this.errorMessage.set('Could not delete interest.'),
    });
  }
}