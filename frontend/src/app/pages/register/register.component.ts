import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../core/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './register.component.html',
  styleUrl: './register.component.css',
})
export class RegisterComponent {
  private readonly fb = inject(FormBuilder);
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  error = '';
  ok = false;

  form = this.fb.nonNullable.group({
    nombre: ['', Validators.required],
    email: ['', [Validators.required, Validators.email]],
    password: ['', [
      Validators.required, 
      Validators.minLength(8), 
      Validators.pattern(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d\w\W]{8,}$/)
    ]],
  });

  submit(): void {
    if (this.form.invalid) return;
    const { nombre: name, email, password } = this.form.getRawValue();
    this.error = '';
    this.ok = false;
    this.auth.register(name, email, password).subscribe({
      next: () => {
        this.ok = true;
        void this.router.navigate(['/login']);
      },
      error: (e) => {
        this.error = e?.error?.detail ?? 'No se pudo registrar.';
      },
    });
  }
}
