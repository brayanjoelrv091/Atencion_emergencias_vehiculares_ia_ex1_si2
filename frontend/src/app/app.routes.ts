import { Routes } from '@angular/router';
import { authGuard } from './guards/auth.guard';
import { roleGuard } from './guards/role.guard';
export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./pages/landing-page/landing-page.component').then((m) => m.LandingPageComponent),
  },

  // ── P1: Autenticación (públicas) ──
  {
    path: 'login',
    loadComponent: () => import('./pages/login/login.component').then((m) => m.LoginComponent),
  },
  {
    path: 'register',
    loadComponent: () => import('./pages/register/register.component').then((m) => m.RegisterComponent),
  },
  {
    path: 'forgot-password',
    loadComponent: () => import('./pages/forgot-password/forgot-password.component').then((m) => m.ForgotPasswordComponent),
  },
  {
    path: 'reset-password',
    loadComponent: () => import('./pages/reset-password/reset-password.component').then((m) => m.ResetPasswordComponent),
  },

  // ── P1: Protegidas ──
  {
    path: 'home',
    loadComponent: () => import('./pages/home/home.component').then((m) => m.HomeComponent),
    canActivate: [authGuard],
  },
  {
    path: 'admin-users',
    loadComponent: () => import('./pages/admin-users/admin-users.component').then((m) => m.AdminUsersComponent),
    canActivate: [authGuard],
  },

  // ── P2: Incidentes ──
  {
    path: 'incidents',
    loadComponent: () => import('./pages/incidents/my-incidents/my-incidents.component').then((m) => m.MyIncidentsComponent),
    canActivate: [authGuard],
  },
  {
    path: 'incidents/report',
    loadComponent: () => import('./pages/incidents/report-incident/report-incident.component').then((m) => m.ReportIncidentComponent),
    canActivate: [authGuard],
  },
  {
    path: 'incidents/:id',
    loadComponent: () => import('./pages/incidents/incident-detail/incident-detail.component').then((m) => m.IncidentDetailComponent),
    canActivate: [authGuard],
  },

  // ── P3: Talleres ──
  {
    path: 'workshops/register',
    loadComponent: () =>
      import('./pages/workshops/register-workshop/register-workshop.component').then((m) => m.RegisterWorkshopComponent),
    canActivate: [authGuard],
  },
  {
    path: 'workshops/requests',
    loadComponent: () =>
      import('./pages/workshops/service-requests/service-requests.component').then((m) => m.ServiceRequestsComponent),
    canActivate: [authGuard],
  },
  {
    path: 'workshops/history',
    loadComponent: () =>
      import('./pages/workshops/service-history/service-history.component').then((m) => m.ServiceHistoryComponent),
    canActivate: [authGuard],
  },

  // ── Catch-all ──
  { path: '**', redirectTo: 'home' },
];
