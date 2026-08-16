import { Component, OnInit, signal } from '@angular/core';
import { ApiService, DocumentSummary } from '../services/api';
import { AuthService } from '../services/auth';

@Component({
  selector: 'app-my-documents',
  standalone: true,
  imports: [],
  templateUrl: './my-documents.html',
  styleUrl: './my-documents.css',
})
export class MyDocuments implements OnInit {
  documents = signal<DocumentSummary[]>([]);
  selectedFile: File | null = null;
  isUploading = signal(false);
  errorMessage = signal<string | null>(null);

  constructor(
    private api: ApiService,
    private auth: AuthService
  ) {}

  ngOnInit(): void {
    this.loadDocuments();
  }

  loadDocuments(): void {
    this.api.getMyDocuments().subscribe({
      next: (docs) => this.documents.set(docs),
      error: () => this.errorMessage.set('Could not load documents.'),
    });
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.selectedFile = input.files?.[0] ?? null;
  }

  upload(): void {
    if (!this.selectedFile) {
      return;
    }

    this.isUploading.set(true);
    this.errorMessage.set(null);

    this.api.uploadDocument(this.selectedFile).subscribe({
      next: () => {
        this.isUploading.set(false);
        this.selectedFile = null;
        this.loadDocuments();
      },
      error: (err) => {
        this.isUploading.set(false);
        this.errorMessage.set(
          err.status === 400
            ? 'File type not allowed. Use PDF, DOC, DOCX, PNG or JPG.'
            : 'Could not upload the file.'
        );
      },
    });
  }

  delete(documentId: number): void {
    if (!confirm('Delete this document?')) {
      return;
    }

    this.api.deleteDocument(documentId).subscribe({
      next: () => this.loadDocuments(),
      error: () => this.errorMessage.set('Could not delete the document.'),
    });
  }

  downloadUrl(documentId: number): string {
    return this.api.documentDownloadUrl(documentId, this.auth.token() ?? '');
  }
}