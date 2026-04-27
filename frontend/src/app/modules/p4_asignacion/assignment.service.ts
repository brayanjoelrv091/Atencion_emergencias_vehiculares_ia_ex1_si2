import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environment';

export interface Assignment {
  id: number;
  incidente_id: number;
  taller_id: number;
  distancia_km: number;
  puntaje: number;
  metodo: string;
  razonamiento: string | null;
  asignado_en: string;
}

export interface Candidate {
  taller_id: number;
  nombre: string;
  distancia_km: number;
  score_distancia: number;
  score_disponibilidad: number;
  score_especialidad: number;
  puntaje_total: number;
}

export interface AutoAssignResponse {
  asignacion: Assignment;
  candidatos_evaluados: Candidate[];
  message: string;
}

@Injectable({ providedIn: 'root' })
export class AssignmentService {
  private readonly http = inject(HttpClient);
  private readonly base = environment.apiUrl;

  /** CU14 — Asignación automática del taller más adecuado. */
  autoAssign(incidentId: number, maxRadius: number = 50): Observable<AutoAssignResponse> {
    return this.http.post<AutoAssignResponse>(
      `${this.base}/assignments/auto/${incidentId}?max_radius_km=${maxRadius}`,
      {},
    );
  }

  /** Ver asignación existente de un incidente. */
  getAssignment(incidentId: number): Observable<Assignment> {
    return this.http.get<Assignment>(`${this.base}/assignments/${incidentId}`);
  }
}
