/// Servicio de Talleres Flutter (P3 — CU10-CU13).
library;

import '../../../core/api_client.dart';
import '../models/workshop_model.dart';

class WorkshopService {
  // ── CU10 — Listar talleres ────────────────────────────────────────

  static Future<List<Workshop>> listAllWorkshops() async {
    return ApiClient.get<List<Workshop>>(
      '/workshops/all',
      fromJson: (j) => (j as List<dynamic>)
          .map((e) => Workshop.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }

  static Future<List<Workshop>> listMyWorkshops() async {
    return ApiClient.get<List<Workshop>>(
      '/workshops',
      fromJson: (j) => (j as List<dynamic>)
          .map((e) => Workshop.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }

  static Future<Workshop> registerWorkshop({
    required String nombre,
    required String direccion,
    required double latitud,
    required double longitud,
    String? telefono,
    String? email,
    List<String>? especialidades,
  }) async {
    return ApiClient.post<Workshop>(
      '/workshops',
      body: {
        'nombre': nombre,
        'direccion': direccion,
        'latitud': latitud,
        'longitud': longitud,
        if (telefono != null) 'telefono': telefono,
        if (email != null) 'email': email,
        if (especialidades != null) 'especialidades': especialidades,
      },
      fromJson: (j) => Workshop.fromJson(j as Map<String, dynamic>),
    );
  }

  // ── CU11 — Solicitudes pendientes ────────────────────────────────

  static Future<List<ServiceRequest>> listPendingRequests(
      int workshopId) async {
    return ApiClient.get<List<ServiceRequest>>(
      '/workshops/$workshopId/requests',
      fromJson: (j) => (j as List<dynamic>)
          .map((e) => ServiceRequest.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }

  // ── CU12 — Actualizar estado ──────────────────────────────────────

  static Future<ServiceRequest> updateStatus(
    int requestId,
    String estado, {
    String? notas,
    int? tecnicoId,
  }) async {
    return ApiClient.patch<ServiceRequest>(
      '/workshops/requests/$requestId/status',
      body: {
        'estado': estado,
        if (notas != null) 'notas': notas,
        if (tecnicoId != null) 'tecnico_id': tecnicoId,
      },
      fromJson: (j) => ServiceRequest.fromJson(j as Map<String, dynamic>),
    );
  }

  // ── CU13 — Historial de atenciones ───────────────────────────────

  static Future<List<ServiceHistory>> getHistory(int workshopId) async {
    return ApiClient.get<List<ServiceHistory>>(
      '/workshops/$workshopId/history',
      fromJson: (j) => (j as List<dynamic>)
          .map((e) => ServiceHistory.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}
