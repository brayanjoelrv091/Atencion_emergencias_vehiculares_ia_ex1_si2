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
    marca: ['', Validators.required],
    modelo: ['', Validators.required],
    placa: ['', Validators.required],
    anio: [null as number | null],
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
    return this.me?.rol === 'cliente';
  }

  get isAdmin(): boolean {
    return this.me?.rol === 'admin';
  }

  get isTaller(): boolean {
    return this.me?.rol === 'taller';
  }

  addVehicle(): void {
    if (!this.isCliente || this.vehicleForm.invalid) return;
    const v = this.vehicleForm.getRawValue();
    this.vehicleError = '';
    this.auth
      .addVehicle({
        marca: v.marca,
        modelo: v.modelo,
        placa: v.placa,
        anio: v.anio ?? undefined,
      })
      .subscribe({
        next: () => {
          this.vehicleForm.reset({ marca: '', modelo: '', placa: '', anio: null });
          this.refresh();
        },
        error: (e) => (this.vehicleError = e?.error?.detail ?? 'No se pudo guardar el vehículo.'),
      });
  }

  removeVehicle(v: Vehicle): void {
    if (!confirm(`Eliminar ${v.placa}?`)) return;
    this.auth.deleteVehicle(v.id).subscribe({ next: () => this.refresh() });
  }

  logout(): void {
    this.auth.logout();
  }
}
