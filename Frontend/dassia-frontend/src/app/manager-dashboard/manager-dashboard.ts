import { Component, OnInit, signal, computed } from '@angular/core';
import { RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ApiService, FeedbackRequestSummary, PendingUser, ComplaintSummary } from '../services/api';
import { AuthService } from '../services/auth';

type ComplaintFilter = 'all' | 'open' | 'resolved';

@Component({
  selector: 'app-manager-dashboard',
  standalone: true,
  imports: [RouterLink, FormsModule],
  templateUrl: './manager-dashboard.html',
  styleUrl: './manager-dashboard.css',
})
export class ManagerDashboard implements OnInit {
  requests = signal<FeedbackRequestSummary[]>([]);
  pendingUsers = signal<PendingUser[]>([]);
  complaints = signal<ComplaintSummary[]>([]);
  loadError = signal<string | null>(null);

  complaintFilter = signal<ComplaintFilter>('all');

  interviewDateInputs: Record<number, string> = {};

  openComplaintsCount = computed(
    () => this.complaints().filter((c) => c.status !== 'Resolved').length
  );
  resolvedComplaintsCount = computed(
    () => this.complaints().filter((c) => c.status === 'Resolved').length
  );

  filteredComplaints = computed(() => {
    const filter = this.complaintFilter();
    const all = this.complaints();
    if (filter === 'open') return all.filter((c) => c.status !== 'Resolved');
    if (filter === 'resolved') return all.filter((c) => c.status === 'Resolved');
    return all;
  });

  constructor(
    private api: ApiService,
    private auth: AuthService
  ) {}

  ngOnInit(): void {
    this.loadRequests();
    this.loadPending();
    this.loadComplaints();
  }

  loadRequests(): void {
    this.api.getFeedbackRequests().subscribe({
      next: (data) => this.requests.set(data),
      error: () => this.loadError.set('Could not load feedback requests.'),
    });
  }

  loadPending(): void {
    this.api.getPendingUsers().subscribe({
      next: (data) => this.pendingUsers.set(data),
      error: () => this.loadError.set('Could not load pending mentor accounts.'),
    });
  }

  loadComplaints(): void {
    this.api.getComplaints().subscribe({
      next: (data) => this.complaints.set(data),
      error: () => this.loadError.set('Could not load complaints.'),
    });
  }

  setComplaintFilter(filter: ComplaintFilter): void {
    this.complaintFilter.set(filter);
  }

  markComplaintResolved(complaintId: number): void {
    this.api.updateComplaintStatus(complaintId, 'Resolved').subscribe({
      next: () => this.loadComplaints(),
      error: () => this.loadError.set('Could not update the complaint.'),
    });
  }

  formatDate(isoString: string): string {
    const date = new Date(isoString);
    if (isNaN(date.getTime())) return isoString;
    return date.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }

  scheduleInterview(userId: number): void {
    const value = this.interviewDateInputs[userId];
    if (!value) {
      this.loadError.set('Choose a date and time first.');
      return;
    }

    this.api.scheduleInterview(userId, new Date(value).toISOString()).subscribe({
      next: () => this.loadPending(),
      error: () => this.loadError.set('Could not schedule the interview.'),
    });
  }

  completeInterview(userId: number): void {
    this.api.completeInterview(userId).subscribe({
      next: () => this.loadPending(),
      error: () => this.loadError.set('Could not mark the interview as completed.'),
    });
  }

  approve(userId: number): void {
    this.api.approveUser(userId).subscribe({
      next: () => this.loadPending(),
      error: (err) => {
        this.loadError.set(
          err.status === 400
            ? 'Interview must be completed before this mentor can be approved.'
            : 'Could not approve this account.'
        );
      },
    });
  }

  reject(userId: number): void {
    if (!confirm('Reject and delete this mentor account? This cannot be undone.')) {
      return;
    }

    this.api.rejectUser(userId).subscribe({
      next: () => this.loadPending(),
      error: () => this.loadError.set('Could not reject this account.'),
    });
  }

  documentDownloadUrl(documentId: number): string {
    return this.api.documentDownloadUrl(documentId, this.auth.token() ?? '');
  }
}