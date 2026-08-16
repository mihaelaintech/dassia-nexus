import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { ApiService } from '../services/api';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [FormsModule, RouterLink],
  templateUrl: './register.html',
  styleUrl: './register.css',
})
export class Register implements OnInit {
  name = '';
  email = '';
  password = '';
  role: 'student' | 'mentor' | 'manager' | 'complaints' = 'student';

  roleLocked = false;

  errorMessage = signal<string | null>(null);
  successMessage = signal<string | null>(null);
  isLoading = signal(false);

  constructor(
    private api: ApiService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    const role = this.route.snapshot.queryParamMap.get('role');
    const valid = ['student', 'mentor', 'manager', 'complaints'];
    if (valid.includes(role ?? '')) {
      this.role = role as any;
      this.roleLocked = true;
    }
  }

  onSubmit(): void {
    this.errorMessage.set(null);
    this.successMessage.set(null);
    this.isLoading.set(true);

    this.api
      .createUser({
        name: this.name,
        email: this.email,
        role: this.role,
        password: this.password,
      })
      .subscribe({
        next: () => {
          this.isLoading.set(false);
          this.successMessage.set('Account created. Redirecting to login...');
          setTimeout(
            () => this.router.navigate(['/login'], { queryParams: { role: this.role } }),
            1200
          );
        },
        error: (err) => {
          this.isLoading.set(false);
          this.errorMessage.set(
            err.status === 409
              ? 'An account with this email already exists.'
              : 'Could not create account. Please check your details and try again.'
          );
        },
      });
  }
}