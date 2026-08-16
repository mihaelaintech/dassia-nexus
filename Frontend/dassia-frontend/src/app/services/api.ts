import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface FeedbackRequestSummary {
  id: number;
  student_name: string;
  title: string;
  description: string;
  status: string;
  mentor_id: number;
  mentor_name?: string;
}

export interface FeedbackComment {
  id: number;
  request_id: number;
  mentor_id: number;
  mentor_name: string | null;
  comment: string;
}

export interface RequestDetailsResponse {
  request: FeedbackRequestSummary;
  comments: FeedbackComment[];
}

export interface MentorProfile {
  id: number;
  name: string;
  expertise?: string;
  bio?: string;
  verified?: boolean;
}

export interface MentorDashboardResponse {
  mentor: MentorProfile;
  assigned_requests: FeedbackRequestSummary[];
}

export interface CurrentUser {
  id: number;
  name: string;
  email: string;
  role: 'student' | 'mentor' | 'manager' | 'complaints';
  mentor_id?: number | null;
  approved: boolean;
}

export interface DocumentSummary {
  id: number;
  original_filename: string;
  uploaded_at: string;
}

export interface PendingUser {
  id: number;
  name: string;
  email: string;
  role: string;
  mentor_id: number | null;
  interview_status: string | null;
  interview_scheduled_at: string | null;
  documents: DocumentSummary[];
}

export interface LoginResponse {
  token: string;
  expires_at: string;
  user: {
    id: number;
    name: string;
    email: string;
    role: 'student' | 'mentor' | 'manager' | 'complaints';
  };
}

export interface MentorCredential {
  id: number;
  type: 'qualification' | 'certification';
  name: string;
  institution?: string;
  year?: number;
}

export interface MentorSkillItem {
  id: number;
  name: string;
}

export interface MentorJob {
  id: number;
  job_title: string;
  employer: string;
  start_year?: number;
  end_year?: number;
  is_current: boolean;
}

export interface MentorFullProfile {
  mentor: {
    id: number;
    name: string;
    expertise?: string;
    bio?: string;
    university?: string;
    qualification_level?: string;
    graduation_year?: number;
    personal_statement?: string;
    interview_scheduled_at?: string | null;
    interview_status: string;
    approved: boolean;
    verified: boolean;
  };
  credentials: MentorCredential[];
  skills: MentorSkillItem[];
  jobs: MentorJob[];
  documents: DocumentSummary[];
}

export interface StudentSkillItem {
  id: number;
  name: string;
}

export interface StudentInterestItem {
  id: number;
  name: string;
}

export interface StudentFullProfile {
  id: number;
  name: string;
  university?: string;
  course?: string;
  year_of_study?: string;
  bio?: string;
  skills: StudentSkillItem[];
  interests: StudentInterestItem[];
}

export interface ComplaintSummary {
  id: number;
  submitted_by_name: string;
  submitted_by_role: string;
  subject: string;
  description: string;
  status: string;
  created_at: string;
}

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private baseUrl = 'http://127.0.0.1:5000';

  constructor(private http: HttpClient) {}

  login(credentials: { email: string; password: string }): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.baseUrl}/login`, credentials);
  }

  logout(): Observable<any> {
    return this.http.post(`${this.baseUrl}/logout`, {});
  }

  me(): Observable<CurrentUser> {
    return this.http.get<CurrentUser>(`${this.baseUrl}/me`);
  }

  meWithToken(token: string): Observable<CurrentUser> {
    return this.http.get<CurrentUser>(`${this.baseUrl}/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
  }

  createUser(user: { name: string; email: string; role: string; password: string }): Observable<any> {
    return this.http.post(`${this.baseUrl}/register`, user);
  }

  getUsers(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/users`);
  }

  createMentor(mentor: { name: string; expertise?: string; bio?: string }): Observable<any> {
    return this.http.post(`${this.baseUrl}/mentors`, mentor);
  }

  getMentors(): Observable<MentorProfile[]> {
    return this.http.get<MentorProfile[]>(`${this.baseUrl}/mentors`);
  }

  getMentorDashboard(mentorId: number): Observable<MentorDashboardResponse> {
    return this.http.get<MentorDashboardResponse>(`${this.baseUrl}/mentor-dashboard/${mentorId}`);
  }

  createFeedbackRequest(payload: {
    title: string;
    description: string;
    mentor_id: number;
  }): Observable<any> {
    return this.http.post(`${this.baseUrl}/feedback-requests`, payload);
  }

  getFeedbackRequests(): Observable<FeedbackRequestSummary[]> {
    return this.http.get<FeedbackRequestSummary[]>(`${this.baseUrl}/feedback-requests`);
  }

  getRequestDetails(requestId: number): Observable<RequestDetailsResponse> {
    return this.http.get<RequestDetailsResponse>(`${this.baseUrl}/feedback-requests/${requestId}`);
  }

  updateRequestStatus(requestId: number, status: string): Observable<any> {
    return this.http.put(`${this.baseUrl}/feedback-requests/${requestId}/status`, { status });
  }

  deleteFeedbackRequest(requestId: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/feedback-requests/${requestId}`);
  }

  addFeedbackComment(payload: { request_id: number; comment: string }): Observable<any> {
    return this.http.post(`${this.baseUrl}/feedback-comments`, payload);
  }

  getFeedbackComments(requestId: number): Observable<FeedbackComment[]> {
    return this.http.get<FeedbackComment[]>(`${this.baseUrl}/feedback-comments/${requestId}`);
  }

  updateFeedbackComment(commentId: number, comment: string): Observable<any> {
    return this.http.put(`${this.baseUrl}/feedback-comments/${commentId}`, { comment });
  }

  deleteFeedbackComment(commentId: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/feedback-comments/${commentId}`);
  }

  uploadDocument(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post(`${this.baseUrl}/documents`, formData);
  }

  getMyDocuments(): Observable<DocumentSummary[]> {
    return this.http.get<DocumentSummary[]>(`${this.baseUrl}/documents/me`);
  }

  getUserDocuments(userId: number): Observable<DocumentSummary[]> {
    return this.http.get<DocumentSummary[]>(`${this.baseUrl}/documents/user/${userId}`);
  }

  deleteDocument(documentId: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/documents/${documentId}`);
  }

  documentDownloadUrl(documentId: number, token: string): string {
    return `${this.baseUrl}/documents/${documentId}/download?token=${token}`;
  }

  getPendingUsers(): Observable<PendingUser[]> {
    return this.http.get<PendingUser[]>(`${this.baseUrl}/users/pending`);
  }

  approveUser(userId: number): Observable<any> {
    return this.http.put(`${this.baseUrl}/users/${userId}/approve`, {});
  }

  rejectUser(userId: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/users/${userId}/reject`);
  }

  updateMentorProfileDetails(mentorId: number, payload: {
    university?: string;
    qualification_level?: string;
    graduation_year?: number;
    personal_statement?: string;
    expertise?: string;
    bio?: string;
  }): Observable<any> {
    return this.http.put(`${this.baseUrl}/mentors/${mentorId}/profile-details`, payload);
  }

  addMentorCredential(mentorId: number, payload: { type: string; name: string; institution?: string; year?: number }): Observable<any> {
    return this.http.post(`${this.baseUrl}/mentors/${mentorId}/credentials`, payload);
  }

  getMentorCredentials(mentorId: number): Observable<MentorCredential[]> {
    return this.http.get<MentorCredential[]>(`${this.baseUrl}/mentors/${mentorId}/credentials`);
  }

  deleteMentorCredential(credentialId: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/mentor-credentials/${credentialId}`);
  }

  addMentorSkill(mentorId: number, name: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/mentors/${mentorId}/skills`, { name });
  }

  getMentorSkillsList(mentorId: number): Observable<MentorSkillItem[]> {
    return this.http.get<MentorSkillItem[]>(`${this.baseUrl}/mentors/${mentorId}/skills`);
  }

  deleteMentorSkill(skillId: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/mentor-skills/${skillId}`);
  }

  addMentorJob(mentorId: number, payload: { job_title: string; employer: string; start_year?: number; end_year?: number; is_current?: boolean }): Observable<any> {
    return this.http.post(`${this.baseUrl}/mentors/${mentorId}/jobs`, payload);
  }

  getMentorJobsList(mentorId: number): Observable<MentorJob[]> {
    return this.http.get<MentorJob[]>(`${this.baseUrl}/mentors/${mentorId}/jobs`);
  }

  deleteMentorJob(jobId: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/mentor-jobs/${jobId}`);
  }

  getMentorFullProfile(mentorId: number): Observable<MentorFullProfile> {
    return this.http.get<MentorFullProfile>(`${this.baseUrl}/mentors/${mentorId}/full`);
  }

  scheduleInterview(userId: number, scheduledAt: string): Observable<any> {
    return this.http.put(`${this.baseUrl}/users/${userId}/interview`, { scheduled_at: scheduledAt });
  }

  completeInterview(userId: number): Observable<any> {
    return this.http.put(`${this.baseUrl}/users/${userId}/interview/complete`, {});
  }

  submitComplaint(payload: { subject: string; description: string }): Observable<any> {
    return this.http.post(`${this.baseUrl}/complaints`, payload);
  }

  getComplaints(): Observable<ComplaintSummary[]> {
    return this.http.get<ComplaintSummary[]>(`${this.baseUrl}/complaints`);
  }

  updateComplaintStatus(complaintId: number, status: string): Observable<any> {
    return this.http.put(`${this.baseUrl}/complaints/${complaintId}/status`, { status });
  }

  getMyStudentProfile(): Observable<StudentFullProfile> {
    return this.http.get<StudentFullProfile>(`${this.baseUrl}/students/me/profile`);
  }

  updateMyStudentProfile(payload: {
    university?: string;
    course?: string;
    year_of_study?: string;
    bio?: string;
  }): Observable<any> {
    return this.http.put(`${this.baseUrl}/students/me/profile`, payload);
  }

  addStudentSkill(name: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/students/me/skills`, { name });
  }

  deleteStudentSkill(skillId: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/student-skills/${skillId}`);
  }

  addStudentInterest(name: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/students/me/interests`, { name });
  }

  deleteStudentInterest(interestId: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/student-interests/${interestId}`);
  }
}
