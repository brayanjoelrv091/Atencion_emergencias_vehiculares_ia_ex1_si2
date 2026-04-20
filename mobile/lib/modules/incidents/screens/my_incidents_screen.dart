/// Pantalla — Lista de Mis Incidentes (CU7, CU14).
library;

import 'package:flutter/material.dart';

import '../../incidents/models/incident_model.dart';
import '../../incidents/services/incident_service.dart';
import '../../assignments/assignment_service.dart';
import '../../../core/api_client.dart';

class MyIncidentsScreen extends StatefulWidget {
  const MyIncidentsScreen({super.key});

  @override
  State<MyIncidentsScreen> createState() => _MyIncidentsScreenState();
}

class _MyIncidentsScreenState extends State<MyIncidentsScreen> {
  List<Incident> _incidents = [];
  bool _loading = true;
  String _error = '';
  String _assignMsg = '';

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() { _loading = true; _error = ''; });
    try {
      final list = await IncidentService.listMyIncidents();
      setState(() => _incidents = list);
    } on ApiException catch (e) {
      setState(() => _error = e.message);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _autoAssign(int incidentId) async {
    setState(() => _assignMsg = '');
    try {
      final res = await AssignmentService.autoAssign(incidentId);
      setState(() => _assignMsg = res.message);
      await _load();
    } on ApiException catch (e) {
      setState(() => _assignMsg = e.message);
    }
  }

  Color _statusColor(String estado) {
    return switch (estado) {
      'nuevo'      => Colors.orange,
      'clasificado' => Colors.blue,
      'asignado'   => Colors.purple,
      'en_proceso' => Colors.amber,
      'resuelto'   => Colors.green,
      _            => Colors.grey,
    };
  }

  Color _severityColor(String? s) {
    return switch (s) {
      'leve'     => const Color(0xFF66BB6A),
      'moderado' => const Color(0xFFFFA726),
      'grave'    => const Color(0xFFEF5350),
      'critico'  => const Color(0xFFFF1744),
      _          => Colors.grey,
    };
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0E1A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF111629),
        title: const Text(
          'Mis Incidentes',
          style: TextStyle(color: Color(0xFF00F2FF), letterSpacing: 1),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Color(0xFF00F2FF)),
            onPressed: _load,
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => Navigator.pushNamed(context, '/report').then((_) => _load()),
        backgroundColor: const Color(0xFF00F2FF),
        foregroundColor: Colors.black,
        icon: const Icon(Icons.add_alert),
        label: const Text('Reportar', style: TextStyle(fontWeight: FontWeight.bold)),
      ),
      body: Column(
        children: [
          if (_assignMsg.isNotEmpty)
            Container(
              color: const Color(0xFF0D3350),
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Text(_assignMsg,
                  style: const TextStyle(color: Color(0xFF00F2FF)),
                  textAlign: TextAlign.center),
            ),
          if (_error.isNotEmpty)
            Container(
              color: const Color(0xFF3B0000),
              padding: const EdgeInsets.all(8),
              child: Text(_error,
                  style: const TextStyle(color: Color(0xFFFF6B6B)),
                  textAlign: TextAlign.center),
            ),
          if (_loading)
            const Expanded(
              child: Center(
                child: CircularProgressIndicator(color: Color(0xFF00F2FF)),
              ),
            )
          else
            Expanded(
              child: _incidents.isEmpty
                  ? const Center(
                      child: Text('Sin incidentes reportados',
                          style: TextStyle(color: Colors.white54)),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.all(12),
                      itemCount: _incidents.length,
                      itemBuilder: (_, i) => _IncidentCard(
                        incident: _incidents[i],
                        statusColor: _statusColor(_incidents[i].estado),
                        severityColor: _severityColor(_incidents[i].severidad),
                        onAssign: _incidents[i].estado == 'clasificado'
                            ? () => _autoAssign(_incidents[i].id)
                            : null,
                        onTap: () => Navigator.pushNamed(
                          context,
                          '/incident-detail',
                          arguments: _incidents[i].id,
                        ),
                      ),
                    ),
            ),
        ],
      ),
    );
  }
}

class _IncidentCard extends StatelessWidget {
  final Incident incident;
  final Color statusColor;
  final Color severityColor;
  final VoidCallback? onAssign;
  final VoidCallback onTap;

  const _IncidentCard({
    required this.incident,
    required this.statusColor,
    required this.severityColor,
    this.onAssign,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.only(bottom: 10),
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: const Color(0xFF111629),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: const Color(0xFF1F2744)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    incident.titulo,
                    style: const TextStyle(
                        color: Colors.white,
                        fontSize: 15,
                        fontWeight: FontWeight.w600),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: statusColor.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: statusColor.withOpacity(0.5)),
                  ),
                  child: Text(
                    incident.estado,
                    style: TextStyle(color: statusColor, fontSize: 11),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                if (incident.categoria != null)
                  _Tag(incident.categoria!, Colors.blue),
                const SizedBox(width: 6),
                if (incident.severidad != null)
                  _Tag(incident.severidad!, severityColor),
                const Spacer(),
                Text(
                  incident.creadoEn.substring(0, 10),
                  style: const TextStyle(color: Colors.white38, fontSize: 11),
                ),
              ],
            ),
            if (onAssign != null) ...[
              const SizedBox(height: 8),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  onPressed: onAssign,
                  icon: const Icon(Icons.location_on, size: 14),
                  label: const Text('Asignar Taller Automáticamente',
                      style: TextStyle(fontSize: 12)),
                  style: OutlinedButton.styleFrom(
                    foregroundColor: const Color(0xFF00F2FF),
                    side: const BorderSide(color: Color(0xFF00F2FF)),
                    padding: const EdgeInsets.symmetric(vertical: 6),
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _Tag extends StatelessWidget {
  final String text;
  final Color color;
  const _Tag(this.text, this.color);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: color.withOpacity(0.4)),
      ),
      child: Text(text, style: TextStyle(color: color, fontSize: 10)),
    );
  }
}
