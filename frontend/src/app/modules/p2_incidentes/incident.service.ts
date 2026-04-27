import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environment';

// ── Interfaces ──

export interface IncidentMedia {
  id: number;
  incidente_id: number;
  tipo_medio: string;
  url_archivo: string;
  subido_en: string;
}

export interface Classification {
  id: number;
  incidente_id: number;
  categoria: string;
  severidad: string;
  confianza: number;
  razonamiento: string | null;
  metodo: string;
  clasificado_en: string;
}

export interface Incident {
  id: number;
  usuario_id: number;
  titulo: string;
  descripcion: string | null;
  estado: string;
  latitud: number;
  longitud: number;
  direccion: string | null;
  url_audio: string | null;
  severidad: string | null;
  categoria: string | null;
  creado_en: string;
  actualizado_en: string | null;
}

export interface IncidentDetail extends Incident {
  medios: IncidentMedia[];
  clasificacion: Classification | null;
}

@Injectable({ providedIn: 'root' })
export class IncidentService {
  private readonly http = inject(HttpClient);
  private readonly base = environment.apiUrl;

  /**
   * CU7 — Reportar incidente con fotos, audio y GPS.
   * Usa FormData para envío multipart.
   */
  reportIncident(
    data: { titulo: string; descripcion?: string; latitud: number; longitud: number; direccion?: string },
    fotos?: File[],
    audio?: File,
  ): Observable<IncidentDetail> {
    const fd = new FormData();
    fd.append('titulo', data.titulo);
    fd.append('latitud', data.latitud.toString());
    fd.append('longitud', data.longitud.toString());
    if (data.descripcion) fd.append('descripcion', data.descripcion);
    if (data.direccion) fd.append('direccion', data.direccion);
    if (fotos) fotos.forEach((f) => fd.append('fotos', f));
    if (audio) fd.append('audio', audio);
    return this.http.post<IncidentDetail>(`${this.base}/incidents`, fd);
  }

  /** Listar mis incidentes. */
  listMyIncidents(): Observable<Incident[]> {
    return this.http.get<Incident[]>(`${this.base}/incidents`);
  }

  /** Listar todos los incidentes (admin). */
  listAllIncidents(): Observable<Incident[]> {
    return this.http.get<Incident[]>(`${this.base}/incidents/all`);
  }

  /** CU9 — Ficha técnica completa. */
  getDetail(incidentId: number): Observable<IncidentDetail> {
    return this.http.get<IncidentDetail>(`${this.base}/incidents/${incidentId}`);
  }

  /** CU8 — Re-clasificar con IA. */
  reclassify(incidentId: number): Observable<Classification> {
    return this.http.post<Classification>(`${this.base}/incidents/${incidentId}/classify`, {});
  }
}
