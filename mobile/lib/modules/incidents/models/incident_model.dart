/// Modelos de Incidentes (P2).
library;

class IncidentMedia {
  final int id;
  final int incidenteId;
  final String tipoMedio;
  final String urlArchivo;
  final String subidoEn;

  const IncidentMedia({
    required this.id,
    required this.incidenteId,
    required this.tipoMedio,
    required this.urlArchivo,
    required this.subidoEn,
  });

  factory IncidentMedia.fromJson(Map<String, dynamic> j) => IncidentMedia(
        id: j['id'] as int,
        incidenteId: j['incidente_id'] as int,
        tipoMedio: j['tipo_medio'] as String,
        urlArchivo: j['url_archivo'] as String,
        subidoEn: j['subido_en'] as String,
      );
}

class Classification {
  final int id;
  final int incidenteId;
  final String categoria;
  final String severidad;
  final double confianza;
  final String? razonamiento;
  final String metodo;
  final String clasificadoEn;

  const Classification({
    required this.id,
    required this.incidenteId,
    required this.categoria,
    required this.severidad,
    required this.confianza,
    this.razonamiento,
    required this.metodo,
    required this.clasificadoEn,
  });

  factory Classification.fromJson(Map<String, dynamic> j) => Classification(
        id: j['id'] as int,
        incidenteId: j['incidente_id'] as int,
        categoria: j['categoria'] as String,
        severidad: j['severidad'] as String,
        confianza: (j['confianza'] as num).toDouble(),
        razonamiento: j['razonamiento'] as String?,
        metodo: j['metodo'] as String,
        clasificadoEn: j['clasificado_en'] as String,
      );
}

class Incident {
  final int id;
  final int usuarioId;
  final String titulo;
  final String? descripcion;
  final String estado;
  final double latitud;
  final double longitud;
  final String? direccion;
  final String? urlAudio;
  final String? severidad;
  final String? categoria;
  final String creadoEn;
  final String? actualizadoEn;

  const Incident({
    required this.id,
    required this.usuarioId,
    required this.titulo,
    this.descripcion,
    required this.estado,
    required this.latitud,
    required this.longitud,
    this.direccion,
    this.urlAudio,
    this.severidad,
    this.categoria,
    required this.creadoEn,
    this.actualizadoEn,
  });

  factory Incident.fromJson(Map<String, dynamic> j) => Incident(
        id: j['id'] as int,
        usuarioId: j['usuario_id'] as int,
        titulo: j['titulo'] as String,
        descripcion: j['descripcion'] as String?,
        estado: j['estado'] as String,
        latitud: (j['latitud'] as num).toDouble(),
        longitud: (j['longitud'] as num).toDouble(),
        direccion: j['direccion'] as String?,
        urlAudio: j['url_audio'] as String?,
        severidad: j['severidad'] as String?,
        categoria: j['categoria'] as String?,
        creadoEn: j['creado_en'] as String,
        actualizadoEn: j['actualizado_en'] as String?,
      );
}

class IncidentDetail extends Incident {
  final List<IncidentMedia> medios;
  final Classification? clasificacion;

  const IncidentDetail({
    required super.id,
    required super.usuarioId,
    required super.titulo,
    super.descripcion,
    required super.estado,
    required super.latitud,
    required super.longitud,
    super.direccion,
    super.urlAudio,
    super.severidad,
    super.categoria,
    required super.creadoEn,
    super.actualizadoEn,
    required this.medios,
    this.clasificacion,
  });

  factory IncidentDetail.fromJson(Map<String, dynamic> j) => IncidentDetail(
        id: j['id'] as int,
        usuarioId: j['usuario_id'] as int,
        titulo: j['titulo'] as String,
        descripcion: j['descripcion'] as String?,
        estado: j['estado'] as String,
        latitud: (j['latitud'] as num).toDouble(),
        longitud: (j['longitud'] as num).toDouble(),
        direccion: j['direccion'] as String?,
        urlAudio: j['url_audio'] as String?,
        severidad: j['severidad'] as String?,
        categoria: j['categoria'] as String?,
        creadoEn: j['creado_en'] as String,
        actualizadoEn: j['actualizado_en'] as String?,
        medios: (j['medios'] as List<dynamic>? ?? [])
            .map((m) => IncidentMedia.fromJson(m as Map<String, dynamic>))
            .toList(),
        clasificacion: j['clasificacion'] != null
            ? Classification.fromJson(
                j['clasificacion'] as Map<String, dynamic>)
            : null,
      );
}
