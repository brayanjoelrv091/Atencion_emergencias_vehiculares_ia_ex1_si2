import { Component, OnInit, AfterViewInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { WebSocketService } from '../../../shared/websocket.service';
import { ActivatedRoute } from '@angular/router';

declare var L: any; // Leaflet Global de index.html

@Component({
  selector: 'app-geo-tracking',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './geo-tracking.component.html',
  styleUrl: './geo-tracking.component.css'
})
export class GeoTrackingComponent implements OnInit, AfterViewInit, OnDestroy {
  map: any;
  markerTecnico: any;
  markerCliente: any;
  incidentId: number = 1;
  status = 'Conectando tracker...';

  constructor(
    private wsService: WebSocketService,
    private route: ActivatedRoute
  ) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) this.incidentId = +id;
  }

  ngAfterViewInit(): void {
    this.initMap();
    this.startTracking();
  }

  initMap() {
    // Coordenadas iniciales (Santa Cruz, Bolivia como fallback)
    this.map = L.map('map-container').setView([-17.7833, -63.1821], 13);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(this.map);

    // Iconos personalizados
    const iconTec = L.icon({
      iconUrl: 'https://cdn-icons-png.flaticon.com/512/3063/3063822.png',
      iconSize: [40, 40]
    });

    const iconCli = L.icon({
      iconUrl: 'https://cdn-icons-png.flaticon.com/512/4433/4433722.png',
      iconSize: [40, 40]
    });

    this.markerTecnico = L.marker([-17.7833, -63.1821], { icon: iconTec }).addTo(this.map).bindPopup('Técnico en camino');
    this.markerCliente = L.marker([-17.7850, -63.1800], { icon: iconCli }).addTo(this.map).bindPopup('Tu ubicación');
  }

  startTracking() {
    this.wsService.connectTracking(this.incidentId).subscribe({
      next: (data) => {
        if (data.type === 'location_update') {
          this.updateMarker(data.role, data.lat, data.lng);
        }
      },
      error: (err) => {
        console.error('Error en WS Tracking', err);
        this.status = 'Error de conexión';
      }
    });
    this.status = 'Tracking activo (Websocket)';
  }

  updateMarker(role: string, lat: number, lng: number) {
    const newLatLng = new L.LatLng(lat, lng);
    if (role === 'tecnico') {
      this.markerTecnico.setLatLng(newLatLng);
      this.status = 'El técnico se está moviendo...';
    } else {
      this.markerCliente.setLatLng(newLatLng);
    }
    this.map.panTo(newLatLng);
  }

  ngOnDestroy(): void {
    // Limpieza si hiciese falta
  }
}
