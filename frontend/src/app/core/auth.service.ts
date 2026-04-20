import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';
import { environment } from '../environment';

const TOKEN_KEY = 'access_token';
const ROLE_KEY = 'user_role';

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface Vehicle {
  id: number;
  usuario_id: number;
  marca: string;
  modelo: string;
  placa: string;
  anio: number | null;
  color: string | null;
}

export interface Me {
  id: number;
  nombre: string;
  email: string;
  telefono: string | null;
  esta_activo: boolean;
  rol: string;
  permisos: Record<string, unknown> | null;
  vehiculos: Vehicle[];
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  private readonly base = environment.apiUrl;

  get token(): string | null {
    return sessionStorage.getItem(TOKEN_KEY);
  }

  isLoggedIn(): boolean {
    return !!this.token;
  }

  login(email: string, password: string): Observable<LoginResponse> {
    return this.http
      .post<LoginResponse>(`${this.base}/auth/login`, { email, password })
      .pipe(
        tap((r) => {
          sessionStorage.setItem(TOKEN_KEY, r.access_token);
          // Decodificar JWT para obtener rol
          try {
            const payload = JSON.parse(atob(r.access_token.split('.')[1]));
            sessionStorage.setItem(ROLE_KEY, payload.role || 'cliente');
          } catch {
            sessionStorage.setItem(ROLE_KEY, 'cliente');
          }
        })
      );
  }

  register(nombre: string, email: string, password: string): Observable<unknown> {
    return this.http.post(`${this.base}/auth/register`, { nombre, email, password });
  }

  logout(): void {
    const t = this.token;
    if (!t) {
      void this.router.navigate(['/login']);
      return;
    }
    this.http.post(`${this.base}/auth/logout`, {}, { headers: { Authorization: `Bearer ${t}` } }).subscribe({
      complete: () => {
        sessionStorage.removeItem(TOKEN_KEY);
        sessionStorage.removeItem(ROLE_KEY);
        void this.router.navigate(['/login']);
      },
      error: () => {
        sessionStorage.removeItem(TOKEN_KEY);
        sessionStorage.removeItem(ROLE_KEY);
        void this.router.navigate(['/login']);
      },
    });
  }

  me(): Observable<Me> {
    return this.http.get<Me>(`${this.base}/me`);
  }

  // CU-04: Recuperar contraseña
  forgotPassword(email: string): Observable<{ message: string; debug_token?: string }> {
    return this.http.post<{ message: string; debug_token?: string }>(`${this.base}/auth/forgot-password`, { email });
  }

  resetPassword(token: string, new_password: string): Observable<void> {
    return this.http.post<void>(`${this.base}/auth/reset-password`, { token, new_password });
  }

  // CU-05: Administración de usuarios y roles
  listUsers(): Observable<Me[]> {
    return this.http.get<Me[]>(`${this.base}/admin/users`);
  }

  updateUserRole(userId: number, rol: string): Observable<Me> {
    return this.http.patch<Me>(`${this.base}/admin/users/${userId}/role`, { rol });
  }

  updateUserPermissions(userId: number, permisos: Record<string, unknown>): Observable<Me> {
    return this.http.patch<Me>(`${this.base}/admin/users/${userId}/permissions`, { permisos });
  }

  addVehicle(body: { marca: string; modelo: string; placa: string; anio?: number | null; color?: string }): Observable<Vehicle> {
    return this.http.post<Vehicle>(`${this.base}/me/vehicles`, body);
  }

  deleteVehicle(id: number): Observable<unknown> {
    return this.http.delete(`${this.base}/me/vehicles/${id}`);
  }
}
