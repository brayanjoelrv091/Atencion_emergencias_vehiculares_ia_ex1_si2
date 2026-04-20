import { SlicePipe } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { WorkshopService, Workshop, ServiceRequest } from '../../../core/workshop.service';

@Component({
  selector: 'app-service-requests',
  standalone: true,
  imports: [RouterLink, SlicePipe],
  templateUrl: './service-requests.component.html',
  styleUrl: './service-requests.component.css',
})
export class ServiceRequestsComponent implements OnInit {
  private readonly wsSvc = inject(WorkshopService);
  workshops: Workshop[] = [];
  requests: ServiceRequest[] = [];
  selectedWorkshop: Workshop | null = null;
  error = '';
  statusMsg = '';

  ngOnInit(): void {
    this.wsSvc.listMyWorkshops().subscribe({
      next: (list) => {
        this.workshops = list;
        if (list.length > 0) this.selectWorkshop(list[0]);
      },
      error: () => (this.error = 'Error al cargar talleres'),
    });
  }

  selectWorkshop(ws: Workshop): void {
    this.selectedWorkshop = ws;
    this.loadRequests(ws.id);
  }

  loadRequests(workshopId: number): void {
    this.wsSvc.listPendingRequests(workshopId).subscribe({
      next: (r) => (this.requests = r),
      error: () => (this.error = 'Error al cargar solicitudes'),
    });
  }

  updateStatus(requestId: number, estado: string): void {
    this.statusMsg = '';
    this.wsSvc.updateRequestStatus(requestId, { estado }).subscribe({
      next: () => {
        this.statusMsg = `Solicitud #${requestId} → ${estado}`;
        if (this.selectedWorkshop) this.loadRequests(this.selectedWorkshop.id);
      },
      error: (e) => (this.error = e?.error?.detail || 'Error al actualizar estado'),
    });
  }
}
