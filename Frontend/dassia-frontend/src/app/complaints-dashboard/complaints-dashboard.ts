import { Component, OnInit, signal, computed } from '@angular/core';
import { ApiService, ComplaintSummary } from '../services/api';

@Component({
  selector: 'app-complaints-dashboard',
  standalone: true,
  imports: [],
  templateUrl: './complaints-dashboard.html',
  styleUrl: './complaints-dashboard.css',
})
export class ComplaintsDashboard implements OnInit {
  complaints = signal<ComplaintSummary[]>([]);
  errorMessage = signal<string | null>(null);

  openCount = computed(
    () => this.complaints().filter((c) => c.status !== 'Resolved').length
  );
  resolvedCount = computed(
    () => this.complaints().filter((c) => c.status === 'Resolved').length
  );

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.api.getComplaints().subscribe({
      next: (data) => this.complaints.set(data),
      error: () => this.errorMessage.set('Could not load complaints.'),
    });
  }

  resolve(id: number): void {
    this.api.updateComplaintStatus(id, 'Resolved').subscribe({
      next: () => this.load(),
      error: () => this.errorMessage.set('Could not update complaint.'),
    });
  }

  reopen(id: number): void {
    this.api.updateComplaintStatus(id, 'Open').subscribe({
      next: () => this.load(),
      error: () => this.errorMessage.set('Could not update complaint.'),
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
}