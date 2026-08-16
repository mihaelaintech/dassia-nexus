import { Routes } from '@angular/router';
import { StudentDashboard } from './student-dashboard/student-dashboard';
import { MentorDashboard } from './mentor-dashboard/mentor-dashboard';
import { ManagerDashboard } from './manager-dashboard/manager-dashboard';
import { ComplaintsDashboard } from './complaints-dashboard/complaints-dashboard';
import { RequestDetails } from './request-details/request-details';
import { Login } from './login/login';
import { Register } from './register/register';
import { PortalSelect } from './portal-select/portal-select';
import { PendingApproval } from './pending-approval/pending-approval';
import { MentorProfileEdit } from './mentor-profile-edit/mentor-profile-edit';
import { MentorProfileView } from './mentor-profile-view/mentor-profile-view';
import { StudentProfileEdit } from './student-profile-edit/student-profile-edit';
import { authGuard, roleGuard } from './auth.guard';

export const routes: Routes = [
  {
    path: 'portal-select',
    component: PortalSelect,
  },
  {
    path: 'login',
    component: Login,
  },
  {
    path: 'register',
    component: Register,
  },
  {
    path: 'pending-approval',
    component: PendingApproval,
    canActivate: [authGuard],
  },
  {
    path: 'my-profile',
    component: MentorProfileEdit,
    canActivate: [authGuard],
  },
  {
    path: 'my-student-profile',
    component: StudentProfileEdit,
    canActivate: [roleGuard('student')],
  },
  {
    path: 'mentor/:id/profile',
    component: MentorProfileView,
    canActivate: [authGuard],
  },
  {
    path: '',
    component: StudentDashboard,
    canActivate: [roleGuard('student')],
  },
  {
    path: 'mentor',
    component: MentorDashboard,
    canActivate: [roleGuard('mentor')],
  },
  {
    path: 'manager',
    component: ManagerDashboard,
    canActivate: [roleGuard('manager')],
  },
  {
    path: 'complaints',
    component: ComplaintsDashboard,
    canActivate: [roleGuard('complaints')],
  },
  {
    path: 'request/:id',
    component: RequestDetails,
    canActivate: [authGuard],
  },
];