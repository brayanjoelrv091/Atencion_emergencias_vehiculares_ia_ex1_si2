import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../core/auth.service';

@Component({
  selector: 'app-forgot-password',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './forgot-password.component.html',
  styleUrl: './forgot-password.component.css',
})
export class ForgotPasswordComponent {
  private readonly auth = inject(AuthService);
  private readonly fb = inject(FormBuilder);

  form = this.fb.nonNullable.group({
    email: ['', [Validators.required, Validators.email]],
  });

  loading = false;
  message = '';
  error = '';
  debugToken = '';

  submit(): void {
    if (this.form.invalid) return;
    this.loading = true;
    this.error = '';
    this.message = '';
    this.debugToken = '';

    this.auth.forgotPassword(this.form.getRawValue().email).subscribe({
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
