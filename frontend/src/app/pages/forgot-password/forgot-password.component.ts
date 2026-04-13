import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../core/auth.service';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './forgot-password.component.html',
  styleUrls: ['./forgot-password.component.css'],
})
export class ForgotPasswordComponent {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  email = '';
  loading = false;
  message = '';
  error = '';
  debugToken = '';

  onSubmit(): void {
    if (!this.email) return;
    this.loading = true;
    this.error = '';
    this.message = '';
    this.debugToken = '';

    this.auth.forgotPassword(this.email).subscribe({
      next: (res) => {
        this.message = res.message;
        if (res.debug_token) {
          this.debugToken = res.debug_token;
        }
        this.loading = false;
      },
      error: (err) => {
        this.error = err.error?.detail || 'Error al procesar la solicitud';
        this.loading = false;
      },
    });
  }
}
