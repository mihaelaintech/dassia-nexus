import { Component, computed } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive, Router } from '@angular/router';
import { AuthService } from './services/auth';
import { ApiService } from './services/api';

interface NavLink {
  path: string;
  label: string;
  icon: string;
  exact: boolean;
}

const NAV_LINKS_BY_ROLE: Record<string, NavLink[]> = {
  student: [
    { path: '/', label: 'Dashboard', icon: '⌂', exact: true },
    { path: '/my-student-profile', label: 'My Profile', icon: '☺', exact: true },
  ],
  mentor: [
    { path: '/mentor', label: 'Dashboard', icon: '⌂', exact: true },
    { path: '/my-profile', label: 'My Profile', icon: '☺', exact: true },
  ],
  manager: [
    { path: '/manager', label: 'Dashboard', icon: '⌂', exact: true },
  ],
  complaints: [
    { path: '/complaints', label: 'Complaints', icon: '✉', exact: true },
  ],
};

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  constructor(
    public auth: AuthService,
    private api: ApiService,
    private router: Router
  ) {}

  navLinks = computed<NavLink[]>(() => {
    const role = this.auth.currentUser()?.role;
    return (role && NAV_LINKS_BY_ROLE[role]) || [];
  });

  roleLabel = computed(() => {
    const role = this.auth.currentUser()?.role;
    if (!role) return '';
    return role.charAt(0).toUpperCase() + role.slice(1);
  });

  initials = computed(() => {
    const name = this.auth.currentUser()?.name ?? '';
    return name
      .split(' ')
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0]?.toUpperCase())
      .join('');
  });

  activeOptions(link: NavLink): { exact: boolean } {
    return { exact: link.exact };
  }

  onLogout(): void {
    this.api.logout().subscribe({
      complete: () => this.finishLogout(),
      error: () => this.finishLogout(),
    });
  }

  private finishLogout(): void {
    this.auth.clearSession();
    this.router.navigate(['/login']);
  }
}