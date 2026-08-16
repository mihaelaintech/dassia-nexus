import { Component, OnInit, signal, computed } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { ApiService, MentorProfile, FeedbackRequestSummary } from '../services/api';
import { MyDocuments } from '../my-documents/my-documents';
import { ComplaintForm } from '../complaint-form/complaint-form';

@Component({
  selector: 'app-student-dashboard',
  standalone: true,
  imports: [FormsModule, MyDocuments, ComplaintForm, RouterLink],
  templateUrl: './student-dashboard.html',
  styleUrl: './student-dashboard.css',
})
export class StudentDashboard implements OnInit {
  feedbackRequests = signal<FeedbackRequestSummary[]>([]);
  mentors = signal<MentorProfile[]>([]);
  showRequestForm = signal(false);

  title = '';
  description = '';
  mentorId: number | null = null;

  isSubmitting = signal(false);
  formError = signal<string | null>(null);
  formSuccess = signal<string | null>(null);

  pendingCount = computed(
    () => this.feedbackRequests().filter((r) => r.status === 'Pending').length
  );
  inProgressCount = computed(
    () => this.feedbackRequests().filter((r) => r.status === 'In Progress').length
  );
  completedCount = computed(
    () => this.feedbackRequests().filter((r) => r.status === 'Completed').length
  );

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.loadRequests();
    this.loadMentors();
  }

  loadRequests(): void {
    this.api.getFeedbackRequests().subscribe({
      next: (data) => this.feedbackRequests.set(data),
      error: (error) => console.error('Error loading feedback requests:', error),
    });
  }

  loadMentors(): void {
    this.api.getMentors().subscribe({
      next: (data) => this.mentors.set(data),
      error: (error) => console.error('Error loading mentors:', error),
    });
  }

  statusBadgeClass(status: string): string {
    switch (status) {
      case 'Pending': return 'badge badge-pending';
      case 'In Progress': return 'badge badge-progress';
      case 'Completed': return 'badge badge-completed';
      default: return 'badge';
    }
  }

  toggleRequestForm(): void {
    this.showRequestForm.set(!this.showRequestForm());
  }

  onSubmit(): void {
    this.formError.set(null);
    this.formSuccess.set(null);

    if (!this.mentorId) {
      this.formError.set('Please choose a mentor.');
      return;
    }

    this.isSubmitting.set(true);

    this.api
      .createFeedbackRequest({
        title: this.title.trim(),
        description: this.description.trim(),
        mentor_id: this.mentorId,
      })
      .subscribe({
        next: () => {
          this.isSubmitting.set(false);
          this.formSuccess.set('Feedback request submitted.');
          this.title = '';
          this.description = '';
          this.mentorId = null;
          this.loadRequests();
        },
        error: (err) => {
          this.isSubmitting.set(false);
          this.formError.set(
            err.status === 400
              ? 'Please fill in every field with a valid mentor.'
              : 'Could not submit the request. Please try again.'
          );
        },
      });
  }
}