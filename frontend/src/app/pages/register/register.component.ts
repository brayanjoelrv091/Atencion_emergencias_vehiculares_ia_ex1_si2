import { Component, inject } from '@angular/core';
import {
  AbstractControl,
  FormBuilder,
  ReactiveFormsModule,
  ValidationErrors,
  ValidatorFn,
  Validators,
} from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../core/auth.service';

/**
 * Req. 3 + Req. 5 — Validador de contraseña segura en el frontend.
 * Regla: mínimo 8 chars · 1 mayúscula · 1 minúscula · 1 número
 * (espeja la regex del backend para feedback inmediato al usuario)
 */
export const passwordStrengthValidator: ValidatorFn = (control: AbstractControl): ValidationErrors | null => {
  const v: string = control.value ?? '';
  if (!v) return null; // Validators.required maneja el vacío
  const regex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;
  return regex.test(v) ? null : { passwordStrength: true };
};

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './register.component.html',
  styleUrl: './register.component.css',
})
export class RegisterComponent {
  private readonly fb   = inject(FormBuilder);
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  error = '';
  ok = false;
  loading = false;

  form = this.fb.nonNullable.group({
    nombre:   ['', [Validators.required, Validators.minLength(2)]],
    email:    ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8), passwordStrengthValidator]],
  });

  get nombreInvalido(): boolean {
    const c = this.form.get('nombre')!;
    return c.invalid && (c.dirty || c.touched);
  }

  get emailInvalido(): boolean {
    const c = this.form.get('email')!;
    return c.invalid && (c.dirty || c.touched);
  }

  get passwordInvalido(): boolean {
    const c = this.form.get('password')!;
    return c.invalid && (c.dirty || c.touched);
  }

  get passwordDebil(): boolean {
    const c = this.form.get('password')!;
    return c.hasError('passwordStrength') && (c.dirty || c.touched);
  }

  submit(): void {
    this.form.markAllAsTouched();
    if (this.form.invalid) return;
    this.loading = true;
    this.error = '';
    this.ok = false;
    const { nombre, email, password } = this.form.getRawValue();
    this.auth.register(nombre, email, password).subscribe({
      next: () => {
        this.ok = true;
        this.loading = false;
        setTimeout(() => void this.router.navigate(['/login']), 1500);
      },
      error: (e) => {
        this.error = e?.error?.detail ?? 'No se pudo registrar.';
        this.loading = false;
      },
    });
  }
}
