import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { ApiService } from '../services/api';
import { AuthService } from '../services/auth';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule, RouterLink],
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class Login implements OnInit {
  email = '';
  password = '';

  expectedRole: 'student' | 'mentor' | 'manager' | null = null;

  private staffRoles = ['manager', 'complaints'];

  errorMessage = signal<string | null>(null);
  isLoading = signal(false);

  constructor(
    private api: ApiService,
    private auth: AuthService,
    private router: Router,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    this.route.queryParamMap.subscribe((params) => {
      const role = params.get('role');
      const valid = ['student', 'mentor', 'manager'];
      this.expectedRole = valid.includes(role ?? '') ? (role as any) : null;
    });
  }

  get portalLabel(): string {
    const labels: Record<string, string> = {
      mentor: 'Mentor Portal',
      student: 'Student Portal',
      manager: 'Staff Portal',
    };
    return this.expectedRole ? labels[this.expectedRole] : '';
  }

  onSubmit(): void {
    this.errorMessage.set(null);
    this.isLoading.set(true);

    this.api.login({ email: this.email, password: this.password }).subscribe({
      next: (loginResponse) => {
        this.checkRoleAndFinish(loginResponse.token);
      },
      error: (err) => {
        this.isLoading.set(false);
        this.errorMessage.set(
          err.status === 401
            ? 'Incorrect email or password.'
            : 'Something went wrong while logging in. Please try again.'
        );
      },
    });
  }

  private checkRoleAndFinish(token: string): void {
    // Fetch the profile using the token directly, WITHOUT touching
    // AuthService yet. This is deliberate: setting the token in
    // AuthService flips the app shell into "logged in" mode immediately,
    // which would tear down this Login component before we've had a
    // chance to verify the role matches the portal the person picked.
    this.api.meWithToken(token).subscribe({
      next: (profile) => {
        const matches =
          !this.expectedRole ||
          (this.expectedRole === 'manager'
            ? this.staffRoles.includes(profile.role)
            : profile.role === this.expectedRole);

        if (!matches) {
          this.isLoading.set(false);
          const labels: Record<string, string> = {
            student: 'Student Login',
            mentor: 'Mentor Login',
            manager: 'Staff Login',
            complaints: 'Staff Login',
          };
          this.errorMessage.set(
            `This account is registered as a ${profile.role}. Please use ${labels[profile.role]} instead.`
          );
          return;
        }

        // Role confirmed - now it's safe to commit the session.
        this.auth.setToken(token);
        this.auth.setUser(profile);
        this.isLoading.set(false);

        if (profile.role === 'mentor' && !profile.approved) {
          this.router.navigate(['/pending-approval']);
          return;
        }

        const destinations: Record<string, string> = {
          mentor: '/mentor',
          manager: '/manager',
          complaints: '/complaints',
          student: '/',
        };
        this.router.navigate([destinations[profile.role]]);
      },
      error: () => {
        this.isLoading.set(false);
        this.errorMessage.set('Logged in, but could not load your profile. Please try again.');
      },
    });
  }
}