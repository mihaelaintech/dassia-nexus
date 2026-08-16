import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ApiService } from '../services/api';
import { AuthService } from '../services/auth';
import { MyDocuments } from '../my-documents/my-documents';
import { ComplaintForm } from '../complaint-form/complaint-form';

@Component({
  selector: 'app-mentor-dashboard',
  imports: [CommonModule, RouterLink, MyDocuments, ComplaintForm],
  templateUrl: './mentor-dashboard.html',
  styleUrl: './mentor-dashboard.css',
})
export class MentorDashboard implements OnInit {
  assignedRequests = signal<any[]>([]);
  loadError = signal<string | null>(null);

  constructor(
    private api: ApiService,
    public auth: AuthService
  ) {}

  ngOnInit(): void {
    this.loadMentorDashboard();
  }

  loadMentorDashboard(): void {
    const mentorId = this.auth.currentUser()?.mentor_id;

    if (!mentorId) {
      this.loadError.set('This mentor account has no linked mentor profile.');
      return;
    }

    this.api.getMentorDashboard(mentorId).subscribe({
      next: (data) => {
        this.assignedRequests.set(data.assigned_requests);
      },
      error: (error) => {
        console.error('Error loading mentor dashboard:', error);
        this.loadError.set('Could not load the mentor dashboard.');
      },
    });
  }
}