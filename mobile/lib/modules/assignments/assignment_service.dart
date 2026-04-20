/// Servicio de Asignación Flutter (P4 — CU14).
library;

import '../../../core/api_client.dart';

class Assignment {
  final int id;
  final int incidenteId;
  final int tallerId;
  final double distanciaKm;
  final double puntaje;
  final String metodo;
  final String? razonamiento;
  final String asignadoEn;

  const Assignment({
    required this.id,
    required this.incidenteId,
    required this.tallerId,
    required this.distanciaKm,
    required this.puntaje,
    required this.metodo,
    this.razonamiento,
    required this.asignadoEn,
  });

  factory Assignment.fromJson(Map<String, dynamic> j) => Assignment(
        id: j['id'] as int,
        incidenteId: j['incidente_id'] as int,
        tallerId: j['taller_id'] as int,
        distanciaKm: (j['distancia_km'] as num).toDouble(),
        puntaje: (j['puntaje'] as num).toDouble(),
        metodo: j['metodo'] as String,
        razonamiento: j['razonamiento'] as String?,
        asignadoEn: j['asignado_en'] as String,
      );
}

class Candidate {
  final int tallerId;
  final String nombre;
  final double distanciaKm;
  final double scoreDistancia;
  final double scoreDisponibilidad;
  final double scoreEspecialidad;
  final double puntajeTotal;

  const Candidate({
    required this.tallerId,
    required this.nombre,
    required this.distanciaKm,
    required this.scoreDistancia,
    required this.scoreDisponibilidad,
    required this.scoreEspecialidad,
    required this.puntajeTotal,
  });

  factory Candidate.fromJson(Map<String, dynamic> j) => Candidate(
        tallerId: j['taller_id'] as int,
        nombre: j['nombre'] as String,
        distanciaKm: (j['distancia_km'] as num).toDouble(),
        scoreDistancia: (j['score_distancia'] as num).toDouble(),
        scoreDisponibilidad: (j['score_disponibilidad'] as num).toDouble(),
        scoreEspecialidad: (j['score_especialidad'] as num).toDouble(),
        puntajeTotal: (j['puntaje_total'] as num).toDouble(),
      );
}

class AutoAssignResult {
  final Assignment asignacion;
  final List<Candidate> candidatosEvaluados;
  final String message;

  const AutoAssignResult({
    required this.asignacion,
    required this.candidatosEvaluados,
    required this.message,
  });

  factory AutoAssignResult.fromJson(Map<String, dynamic> j) => AutoAssignResult(
        asignacion: Assignment.fromJson(
            j['asignacion'] as Map<String, dynamic>),
        candidatosEvaluados:
            (j['candidatos_evaluados'] as List<dynamic>? ?? [])
                .map((c) => Candidate.fromJson(c as Map<String, dynamic>))
                .toList(),
        message: j['message'] as String,
      );
}

class AssignmentService {
  /// CU14 — Asignación automática del taller más adecuado.
  static Future<AutoAssignResult> autoAssign(
    int incidentId, {
    double maxRadiusKm = 50.0,
  }) async {
    return ApiClient.post<AutoAssignResult>(
      '/assignments/auto/$incidentId?max_radius_km=$maxRadiusKm',
      fromJson: (j) => AutoAssignResult.fromJson(j as Map<String, dynamic>),
    );
  }

  /// Ver asignación existente de un incidente.
  static Future<Assignment> getAssignment(int incidentId) async {
    return ApiClient.get<Assignment>(
      '/assignments/$incidentId',
      fromJson: (j) => Assignment.fromJson(j as Map<String, dynamic>),
    );
  }
}
