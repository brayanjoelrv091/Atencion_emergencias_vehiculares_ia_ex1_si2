import { Component, OnInit, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { AuthService, Me, Vehicle } from '../../core/auth.service';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css',
})
export class HomeComponent implements OnInit {
  private readonly auth = inject(AuthService);
  private readonly fb = inject(FormBuilder);

  me: Me | null = null;
  loadError = '';
  vehicleError = '';

  vehicleForm = this.fb.nonNullable.group({
    brand: ['', Validators.required],
    model: ['', Validators.required],
    license_plate: ['', Validators.required],
    year: [null as number | null],
  });

  ngOnInit(): void {
    this.refresh();
  }

  refresh(): void {
    this.loadError = '';
    this.auth.me().subscribe({
      next: (m) => (this.me = m),
      error: () => (this.loadError = 'No se pudo cargar el perfil.'),
    });
  }

  get isCliente(): boolean {
    return this.me?.role === 'cliente';
  }

  get isAdmin(): boolean {
    return this.me?.role === 'admin';
  }

  addVehicle(): void {
    if (!this.isCliente || this.vehicleForm.invalid) return;
    const v = this.vehicleForm.getRawValue();
    this.vehicleError = '';
    this.auth
      .addVehicle({
        brand: v.brand,
        model: v.model,
        license_plate: v.license_plate,
        year: v.year ?? undefined,
      })
      .subscribe({
        next: () => {
          this.vehicleForm.reset({ brand: '', model: '', license_plate: '', year: null });
          this.refresh();
        },
        error: (e) => (this.vehicleError = e?.error?.detail ?? 'No se pudo guardar el vehículo.'),
      });
  }

  removeVehicle(v: Vehicle): void {
    if (!confirm(`Eliminar ${v.license_plate}?`)) return;
    this.auth.deleteVehicle(v.id).subscribe({ next: () => this.refresh() });
  }

  logout(): void {
    this.auth.logout();
  }
}
