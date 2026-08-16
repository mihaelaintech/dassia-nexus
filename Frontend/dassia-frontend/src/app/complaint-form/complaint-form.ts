import { Component, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../services/api';

@Component({
  selector: 'app-complaint-form',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './complaint-form.html',
  styleUrl: './complaint-form.css',
})
export class ComplaintForm {
  subject = '';
  description = '';
  isSubmitting = signal(false);
  successMessage = signal<string | null>(null);
  errorMessage = signal<string | null>(null);

  constructor(private api: ApiService) {}

  submit(): void {
    if (!this.subject.trim() || !this.description.trim()) return;

    this.isSubmitting.set(true);
    this.successMessage.set(null);
    this.errorMessage.set(null);

    this.api.submitComplaint({ subject: this.subject.trim(), description: this.description.trim() }).subscribe({
      next: () => {
        this.isSubmitting.set(false);
        this.successMessage.set('Complaint submitted.');
        this.subject = '';
        this.description = '';
      },
      error: () => {
        this.isSubmitting.set(false);
        this.errorMessage.set('Could not submit complaint.');
      },
    });
  }
}