/// Servicio de Incidentes Flutter (P2 — CU7-CU9).
library;

import 'dart:io';

import '../../../core/api_client.dart';
import '../models/incident_model.dart';

class IncidentService {
  // ── CU7 — Reportar incidente con fotos/audio/GPS ─────────────────

  static Future<IncidentDetail> reportIncident({
    required String titulo,
    required double latitud,
    required double longitud,
    String? descripcion,
    String? direccion,
    List<File>? fotos,
    File? audio,
  }) async {
    final fields = <String, String>{
      'titulo': titulo,
      'latitud': latitud.toString(),
      'longitud': longitud.toString(),
      ...?descripcion == null ? null : {'descripcion': descripcion},
      ...?direccion == null ? null : {'direccion': direccion},
    };

    final files = <MapEntry<String, File>>[];
    if (fotos != null) {
      for (final f in fotos.take(5)) {
        files.add(MapEntry('fotos', f));
      }
    }
    if (audio != null) {
      files.add(MapEntry('audio', audio));
    }

    return ApiClient.postMultipart<IncidentDetail>(
      '/incidents',
      fields: fields,
      files: files.isNotEmpty ? files : null,
      fromJson: (j) => IncidentDetail.fromJson(j as Map<String, dynamic>),
    );
  }

  // ── Listar mis incidentes ─────────────────────────────────────────

  static Future<List<Incident>> listMyIncidents() async {
    return ApiClient.get<List<Incident>>(
      '/incidents',
      fromJson: (j) => (j as List<dynamic>)
          .map((e) => Incident.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }

  // ── CU9 — Ficha técnica del incidente ────────────────────────────

  static Future<IncidentDetail> getDetail(int incidentId) async {
    return ApiClient.get<IncidentDetail>(
      '/incidents/$incidentId',
      fromJson: (j) => IncidentDetail.fromJson(j as Map<String, dynamic>),
    );
  }

  // ── CU8 — Re-clasificar con IA ───────────────────────────────────

  static Future<Classification> reclassify(int incidentId) async {
    return ApiClient.post<Classification>(
      '/incidents/$incidentId/classify',
      fromJson: (j) => Classification.fromJson(j as Map<String, dynamic>),
    );
  }
}
