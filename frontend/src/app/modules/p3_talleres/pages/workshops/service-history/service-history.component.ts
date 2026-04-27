import { SlicePipe } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { WorkshopService, Workshop, ServiceHistory } from '../../../workshop.service';

@Component({
  selector: 'app-service-history',
  standalone: true,
  imports: [SlicePipe],
  templateUrl: './service-history.component.html',
  styleUrl: './service-history.component.css',
})
export class ServiceHistoryComponent implements OnInit {
  private readonly wsSvc = inject(WorkshopService);
  workshops: Workshop[] = [];
  history: ServiceHistory[] = [];
  selectedId = 0;
  error = '';

  ngOnInit(): void {
    this.wsSvc.listMyWorkshops().subscribe({
      next: (list) => {
        this.workshops = list;
        if (list.length) { this.selectedId = list[0].id; this.loadHistory(this.selectedId); }
      },
    });
  }
  loadHistory(wsId: number): void {
    this.selectedId = wsId;
    this.wsSvc.getServiceHistory(wsId).subscribe({
      next: (h) => (this.history = h),
      error: () => (this.error = 'Error al cargar historial'),
    });
  }
}
