import { Component, OnInit } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../services/auth';
import { MyDocuments } from '../my-documents/my-documents';

@Component({
  selector: 'app-pending-approval',
  standalone: true,
  imports: [MyDocuments, RouterLink],
  templateUrl: './pending-approval.html',
  styleUrl: './pending-approval.css',
})
export class PendingApproval implements OnInit {
  constructor(
    public auth: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    if (this.auth.currentUser()?.approved) {
      this.router.navigate(['/mentor']);
    }
  }
}