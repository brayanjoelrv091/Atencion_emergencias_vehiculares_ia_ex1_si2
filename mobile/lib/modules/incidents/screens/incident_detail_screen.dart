library;

import 'package:flutter/material.dart';

import '../../../core/api_client.dart';
import '../../assignments/assignment_service.dart';
import '../models/incident_model.dart';
import '../services/incident_service.dart';

class IncidentDetailScreen extends StatefulWidget {
  const IncidentDetailScreen({super.key});

  @override
  State<IncidentDetailScreen> createState() => _IncidentDetailScreenState();
}

class _IncidentDetailScreenState extends State<IncidentDetailScreen> {
  IncidentDetail? _detail;
  Assignment? _assignment;
  bool _loading = true;
  String _error = '';
  bool _loadedFromArgs = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_loadedFromArgs) return;
    _loadedFromArgs = true;

    final incidentId = ModalRoute.of(context)?.settings.arguments as int?;
    if (incidentId == null) {
      setState(() {
        _loading = false;
        _error = 'No se recibio el ID del incidente.';
      });
      return;
    }
    _load(incidentId);
  }

  Future<void> _load(int incidentId) async {
    setState(() {
      _loading = true;
      _error = '';
    });

    try {
      final detail = await IncidentService.getDetail(incidentId);
      Assignment? assignment;
      if ({
        'asignado',
        'en_proceso',
        'resuelto',
      }.contains(detail.estado)) {
        try {
          assignment = await AssignmentService.getAssignment(incidentId);
        } on ApiException {
          assignment = null;
        }
      }

      if (!mounted) return;
      setState(() {
        _detail = detail;
        _assignment = assignment;
      });
    } on ApiException catch (e) {
      if (!mounted) return;
      setState(() => _error = e.message);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0E1A),
      appBar: AppBar(title: const Text('Detalle del Incidente')),
      body: _loading
          ? const Center(
              child: CircularProgressIndicator(color: Color(0xFF00F2FF)),
            )
          : _error.isNotEmpty
          ? Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Text(
                  _error,
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Color(0xFFFF6B6B)),
                ),
              ),
            )
          : _detail == null
          ? const Center(
              child: Text(
                'No hay informacion disponible.',
                style: TextStyle(color: Colors.white54),
              ),
            )
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                _SectionCard(
                  title: _detail!.titulo,
                  children: [
                    _InfoRow('Estado', _detail!.estado),
                    _InfoRow('Categoria', _detail!.categoria ?? 'Sin clasificar'),
                    _InfoRow('Severidad', _detail!.severidad ?? 'Sin determinar'),
                    _InfoRow('Fecha', _detail!.creadoEn.substring(0, 19)),
                    if (_detail!.descripcion != null)
                      _InfoRow('Descripcion', _detail!.descripcion!),
                  ],
                ),
                const SizedBox(height: 12),
                _SectionCard(
                  title: 'Ubicacion',
                  children: [
                    _InfoRow('Latitud', _detail!.latitud.toString()),
                    _InfoRow('Longitud', _detail!.longitud.toString()),
                    if (_detail!.direccion != null)
                      _InfoRow('Direccion', _detail!.direccion!),
                  ],
                ),
                if (_detail!.clasificacion != null) ...[
                  const SizedBox(height: 12),
                  _SectionCard(
                    title: 'Clasificacion IA',
                    children: [
                      _InfoRow('Metodo', _detail!.clasificacion!.metodo),
                      _InfoRow(
                        'Confianza',
                        '${(_detail!.clasificacion!.confianza * 100).toStringAsFixed(1)}%',
                      ),
                      if (_detail!.clasificacion!.razonamiento != null)
                        _InfoRow(
                          'Resumen',
                          _detail!.clasificacion!.razonamiento!,
                        ),
                    ],
                  ),
                ],
                if (_assignment != null) ...[
                  const SizedBox(height: 12),
                  _SectionCard(
                    title: 'Asignacion',
                    children: [
                      _InfoRow('Taller ID', _assignment!.tallerId.toString()),
                      _InfoRow(
                        'Distancia',
                        '${_assignment!.distanciaKm.toStringAsFixed(2)} km',
                      ),
                      _InfoRow('Metodo', _assignment!.metodo),
                      if (_assignment!.razonamiento != null)
                        _InfoRow('Detalle', _assignment!.razonamiento!),
                    ],
                  ),
                ],
                if (_detail!.medios.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  _SectionCard(
                    title: 'Archivos Adjuntos',
                    children: _detail!.medios
                        .map(
                          (media) => _InfoRow(
                            media.tipoMedio.toUpperCase(),
                            media.urlArchivo,
                          ),
                        )
                        .toList(),
                  ),
                ],
                const SizedBox(height: 24),
                if ({'asignado', 'en_proceso'}.contains(_detail!.estado))
                  ElevatedButton.icon(
                    onPressed: () {
                      Navigator.pushNamed(
                        context,
                        '/tracking',
                        arguments: {
                          'incidentId': _detail!.id,
                          'role': 'cliente',
                        },
                      );
                    },
                    icon: const Icon(Icons.location_on),
                    label: const Text('📍 VER TRACKING GPS'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF00F2FF),
                      foregroundColor: Colors.black,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      textStyle: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ),
                if (_detail!.estado == 'resuelto')
                  ElevatedButton.icon(
                    onPressed: () {
                      Navigator.pushNamed(
                        context,
                        '/payment',
                        arguments: {
                          'incidentId': _detail!.id,
                          'amount': 50000.0, // Monto simulado
                        },
                      );
                    },
                    icon: const Icon(Icons.payment),
                    label: const Text('💳 PAGAR SERVICIO'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.greenAccent,
                      foregroundColor: Colors.black,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      textStyle: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ),
              ],
            ),
    );
  }
}

class _SectionCard extends StatelessWidget {
  final String title;
  final List<Widget> children;

  const _SectionCard({
    required this.title,
    required this.children,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF111629),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF1F2744)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(
              color: Color(0xFF00F2FF),
              fontSize: 16,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 12),
          ...children,
        ],
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final String label;
  final String value;

  const _InfoRow(this.label, this.value);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: const TextStyle(color: Colors.white54, fontSize: 12),
          ),
          const SizedBox(height: 2),
          Text(
            value,
            style: const TextStyle(color: Colors.white, fontSize: 14),
          ),
        ],
      ),
    );
  }
}
