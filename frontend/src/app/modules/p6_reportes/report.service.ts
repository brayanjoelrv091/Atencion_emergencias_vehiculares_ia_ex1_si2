import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environment';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ReportService {
  private apiUrl = `${environment.apiUrl}/reports`;

  constructor(private http: HttpClient) {}

  getIncidentsPdf(): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/incidents/pdf`, { responseType: 'blob' });
  }

  getIncidentsExcel(): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/incidents/excel`, { responseType: 'blob' });
  }

  getHistory(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/history`);
  }
}
