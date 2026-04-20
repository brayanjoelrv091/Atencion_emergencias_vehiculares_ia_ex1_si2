import { SlicePipe } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { IncidentDetail, IncidentService } from '../../../core/incident.service';
import { AssignmentService, Assignment } from '../../../core/assignment.service';

@Component({
  selector: 'app-incident-detail',
  standalone: true,
  imports: [RouterLink, SlicePipe],
  templateUrl: './incident-detail.component.html',
  styleUrl: './incident-detail.component.css',
})
export class IncidentDetailComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly incidentSvc = inject(IncidentService);
  private readonly assignmentSvc = inject(AssignmentService);

  detail: IncidentDetail | null = null;
  assignment: Assignment | null = null;
  error = '';

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (id) this.loadDetail(id);
  }

  loadDetail(id: number): void {
    this.incidentSvc.getDetail(id).subscribe({
      next: (d) => {
        this.detail = d;
        if (d.estado === 'asignado' || d.estado === 'en_proceso' || d.estado === 'resuelto') {
          this.loadAssignment(id);
        }
      },
      error: () => (this.error = 'Error al cargar incidente'),
    });
  }

  loadAssignment(incidentId: number): void {
    this.assignmentSvc.getAssignment(incidentId).subscribe({
      next: (a) => (this.assignment = a),
      error: () => {},
    });
  }
}
