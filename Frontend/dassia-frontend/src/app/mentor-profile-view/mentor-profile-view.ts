import { Component, OnInit, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ApiService, MentorFullProfile } from '../services/api';

@Component({
  selector: 'app-mentor-profile-view',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './mentor-profile-view.html',
  styleUrl: './mentor-profile-view.css',
})
export class MentorProfileView implements OnInit {
  profile = signal<MentorFullProfile | null>(null);
  errorMessage = signal<string | null>(null);
  isLoading = signal(true);

  constructor(
    private route: ActivatedRoute,
    private api: ApiService
  ) {}

  ngOnInit(): void {
    const idParam = this.route.snapshot.paramMap.get('id');
    const mentorId = idParam ? Number(idParam) : null;

    if (!mentorId) {
      this.errorMessage.set('Invalid mentor.');
      this.isLoading.set(false);
      return;
    }

    this.api.getMentorFullProfile(mentorId).subscribe({
      next: (data) => {
        this.profile.set(data);
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('Could not load this mentor profile.');
        this.isLoading.set(false);
      },
    });
  }

  initials(name: string): string {
    return name
      .split(' ')
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0]?.toUpperCase())
      .join('');
  }
}