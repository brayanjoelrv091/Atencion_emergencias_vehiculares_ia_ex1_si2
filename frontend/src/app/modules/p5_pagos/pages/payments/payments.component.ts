import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { PaymentService, Pago } from '../../payment.service';

@Component({
  selector: 'app-payments',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './payments.component.html',
  styleUrl: './payments.component.css'
})
export class PaymentsComponent {
  pago: Pago = {
    incidente_id: 0,
    monto: 50.00,
    metodo_pago: 'tarjeta'
  };
  tarjeta = {
    numero: '',
    expira: '',
    cvv: '',
    titular: ''
  };
  procesando = false;
  exito = false;
  error = '';

  constructor(
    private paymentService: PaymentService,
    private route: ActivatedRoute,
  ) {
    const incidentId = Number(this.route.snapshot.queryParamMap.get('incidentId'));
    const amount = Number(this.route.snapshot.queryParamMap.get('amount'));
    if (Number.isFinite(incidentId) && incidentId > 0) {
      this.pago.incidente_id = incidentId;
    }
    if (Number.isFinite(amount) && amount > 0) {
      this.pago.monto = amount;
    }
  }

  confirmarPago() {
    if (this.pago.incidente_id <= 0 || this.pago.monto <= 0) {
      this.error = 'Ingresa un ID de incidente y un monto validos.';
      return;
    }
    this.procesando = true;
    this.error = '';
    this.paymentService.processPayment(this.pago).subscribe({
      next: (resp) => {
        console.log('Pago exitoso', resp);
        this.procesando = false;
        this.exito = true;
      },
      error: (err) => {
        console.error('Error al pagar', err);
        this.procesando = false;
        this.error = err?.error?.detail || 'Error en la pasarela simulada';
      }
    });
  }
}
