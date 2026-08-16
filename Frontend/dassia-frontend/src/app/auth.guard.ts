import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from './services/auth';

export const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);

  if (auth.isLoggedIn()) {
    return true;
  }

  router.navigate(['/portal-select']);
  return false;
};

export const roleGuard = (requiredRole: 'student' | 'mentor' | 'manager' | 'complaints'): CanActivateFn => {
  return () => {
    const auth = inject(AuthService);
    const router = inject(Router);

    if (!auth.isLoggedIn()) {
      router.navigate(['/portal-select']);
      return false;
    }

    if (auth.currentUser()?.role !== requiredRole) {
      const role = auth.currentUser()?.role;
      const routes: Record<string, string> = {
        mentor: '/mentor',
        manager: '/manager',
        complaints: '/complaints',
        student: '/',
      };
      router.navigate([role ? routes[role] : '/portal-select']);
      return false;
    }

    if (requiredRole === 'mentor' && !auth.currentUser()?.approved) {
      router.navigate(['/pending-approval']);
      return false;
    }

    return true;
  };
};