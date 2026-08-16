import { Injectable, signal } from '@angular/core';
import { CurrentUser } from './api';

const TOKEN_KEY = 'dassia_token';
const USER_KEY = 'dassia_user';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  token = signal<string | null>(localStorage.getItem(TOKEN_KEY));
  currentUser = signal<CurrentUser | null>(this.readStoredUser());

  private readStoredUser(): CurrentUser | null {
    const raw = localStorage.getItem(USER_KEY);
    if (!raw) {
      return null;
    }
    try {
      return JSON.parse(raw) as CurrentUser;
    } catch {
      return null;
    }
  }

  setToken(token: string): void {
    this.token.set(token);
    localStorage.setItem(TOKEN_KEY, token);
  }

  setUser(user: CurrentUser): void {
    this.currentUser.set(user);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }

  isLoggedIn(): boolean {
    return !!this.token();
  }

  clearSession(): void {
    this.token.set(null);
    this.currentUser.set(null);
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }
}