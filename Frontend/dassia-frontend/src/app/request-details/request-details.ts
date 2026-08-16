import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import {
  ApiService,
  FeedbackRequestSummary,
  FeedbackComment,
} from '../services/api';
import { AuthService } from '../services/auth';

@Component({
  selector: 'app-request-details',
  imports: [CommonModule, FormsModule],
  templateUrl: './request-details.html',
  styleUrl: './request-details.css',
})
export class RequestDetails implements OnInit {
  requestId!: number;

  requestData = signal<FeedbackRequestSummary | null>(null);
  comments = signal<FeedbackComment[]>([]);
  isLoading = signal(true);
  isSubmittingComment = signal(false);
  isUpdatingStatus = signal(false);
  isDeletingRequest = signal(false);
  errorMessage = signal('');

  newComment = '';

  readonly allStatuses = ['Pending', 'In Progress', 'Completed'];

  readonly nextStatusMap: Record<string, string | null> = {
    Pending: 'In Progress',
    'In Progress': 'Completed',
    Completed: null,
  };

  editingCommentId: number | null = null;
  editingText = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private apiService: ApiService,
    public auth: AuthService
  ) {}

  get isManager(): boolean {
    return this.auth.currentUser()?.role === 'manager';
  }

  ngOnInit(): void {
    this.requestId = Number(this.route.snapshot.paramMap.get('id'));
    this.loadDetails();
  }

  loadDetails(): void {
    this.isLoading.set(true);
    this.errorMessage.set('');

    this.apiService.getRequestDetails(this.requestId).subscribe({
      next: (data) => {
        this.requestData.set(data.request);
        this.comments.set(data.comments);
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('Unable to load this feedback request.');
        this.isLoading.set(false);
      },
    });
  }

  refreshComments(): void {
    this.apiService.getFeedbackComments(this.requestId).subscribe({
      next: (comments) => this.comments.set(comments),
      error: () => this.errorMessage.set('Unable to refresh comments.'),
    });
  }

  submitComment(): void {
    if (!this.newComment.trim()) {
      return;
    }

    this.isSubmittingComment.set(true);
    this.apiService
      .addFeedbackComment({
        request_id: this.requestId,
        comment: this.newComment.trim(),
      })
      .subscribe({
        next: () => {
          this.newComment = '';
          this.isSubmittingComment.set(false);
          this.refreshComments();
        },
        error: () => {
          this.errorMessage.set('Unable to submit comment.');
          this.isSubmittingComment.set(false);
        },
      });
  }

  get nextStatus(): string | null {
    const current = this.requestData();
    return current ? this.nextStatusMap[current.status] : null;
  }

  advanceStatus(): void {
    if (!this.nextStatus) {
      return;
    }
    this.setStatus(this.nextStatus);
  }

  setStatus(status: string): void {
    const current = this.requestData();
    if (!current || status === current.status) {
      return;
    }

    this.isUpdatingStatus.set(true);
    this.apiService.updateRequestStatus(this.requestId, status).subscribe({
      next: () => {
        this.requestData.update((r) => (r ? { ...r, status } : r));
        this.isUpdatingStatus.set(false);
      },
      error: () => {
        this.errorMessage.set('Unable to update status.');
        this.isUpdatingStatus.set(false);
      },
    });
  }

  deleteRequest(): void {
    if (!confirm('Delete this feedback request and all its comments? This cannot be undone.')) {
      return;
    }

    this.isDeletingRequest.set(true);
    this.apiService.deleteFeedbackRequest(this.requestId).subscribe({
      next: () => this.router.navigate(['/manager']),
      error: () => {
        this.errorMessage.set('Unable to delete this request.');
        this.isDeletingRequest.set(false);
      },
    });
  }

  startEditComment(comment: FeedbackComment): void {
    this.editingCommentId = comment.id;
    this.editingText = comment.comment;
  }

  cancelEditComment(): void {
    this.editingCommentId = null;
    this.editingText = '';
  }

  saveEditComment(commentId: number): void {
    if (!this.editingText.trim()) {
      return;
    }

    this.apiService.updateFeedbackComment(commentId, this.editingText.trim()).subscribe({
      next: () => {
        this.editingCommentId = null;
        this.editingText = '';
        this.refreshComments();
      },
      error: () => this.errorMessage.set('Unable to update comment.'),
    });
  }

  deleteComment(commentId: number): void {
    if (!confirm('Delete this comment?')) {
      return;
    }

    this.apiService.deleteFeedbackComment(commentId).subscribe({
      next: () => this.refreshComments(),
      error: () => this.errorMessage.set('Unable to delete comment.'),
    });
  }

  goBackToDashboard(): void {
    this.router.navigate([this.isManager ? '/manager' : '/mentor']);
  }
}