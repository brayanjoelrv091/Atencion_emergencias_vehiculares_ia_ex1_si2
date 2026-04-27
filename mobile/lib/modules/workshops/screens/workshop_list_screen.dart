/// CU10-CU13 — Pantalla principal de Talleres.
///
/// Muestra lista de todos los talleres activos (GET /workshops/all).
/// Rol taller: puede ver sus solicitudes pendientes y acceder al historial.
/// Rol admin/taller: puede registrar un nuevo taller.
library;

import 'package:flutter/material.dart';

import '../../../core/api_client.dart';
import '../models/workshop_model.dart';
import '../services/workshop_service.dart';
import 'workshop_requests_screen.dart';
import 'workshop_history_screen.dart';
import 'register_workshop_screen.dart';

class WorkshopListScreen extends StatefulWidget {
  const WorkshopListScreen({super.key});

  @override
  State<WorkshopListScreen> createState() => _WorkshopListScreenState();
}

class _WorkshopListScreenState extends State<WorkshopListScreen> {
  List<Workshop> _workshops = [];
  bool _loading = true;
  String _error = '';

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = '';
    });
    try {
      final list = await WorkshopService.listAllWorkshops();
      setState(() => _workshops = list);
    } on ApiException catch (e) {
      setState(() => _error = e.message);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0E1A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF111629),
        title: const Text(
          'Talleres',
          style: TextStyle(color: Color(0xFF0096FF), letterSpacing: 1),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Color(0xFF0096FF)),
            onPressed: _load,
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => Navigator.push(
          context,
          MaterialPageRoute(builder: (_) => const RegisterWorkshopScreen()),
        ).then((_) => _load()),
        backgroundColor: const Color(0xFF0096FF),
        foregroundColor: Colors.white,
        icon: const Icon(Icons.add_business),
        label: const Text('Registrar', style: TextStyle(fontWeight: FontWeight.bold)),
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_loading) {
      return const Center(child: CircularProgressIndicator(color: Color(0xFF0096FF)));
    }
    if (_error.isNotEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.error_outline, color: Color(0xFFFF6B6B), size: 48),
              const SizedBox(height: 12),
              Text(_error, style: const TextStyle(color: Color(0xFFFF6B6B))),
              const SizedBox(height: 16),
              ElevatedButton(onPressed: _load, child: const Text('Reintentar')),
            ],
          ),
        ),
      );
    }
    if (_workshops.isEmpty) {
      return const Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.store_outlined, color: Colors.white24, size: 64),
            SizedBox(height: 16),
            Text('Sin talleres registrados', style: TextStyle(color: Colors.white54, fontSize: 16)),
          ],
        ),
      );
    }
    return RefreshIndicator(
      onRefresh: _load,
      color: const Color(0xFF0096FF),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _workshops.length,
        itemBuilder: (_, i) => _WorkshopCard(
          workshop: _workshops[i],
          onRequests: () => Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => WorkshopRequestsScreen(workshop: _workshops[i]),
            ),
          ),
          onHistory: () => Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => WorkshopHistoryScreen(workshop: _workshops[i]),
            ),
          ),
        ),
      ),
    );
  }
}

class _WorkshopCard extends StatelessWidget {
  final Workshop workshop;
  final VoidCallback onRequests;
  final VoidCallback onHistory;

  const _WorkshopCard({
    required this.workshop,
    required this.onRequests,
    required this.onHistory,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: const Color(0xFF111629),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: workshop.estaActivo
              ? const Color(0xFF0096FF).withValues(alpha: 0.3)
              : Colors.white12,
        ),
      ),
      child: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: const Color(0xFF0096FF).withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(Icons.build, color: Color(0xFF0096FF), size: 26),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              workshop.nombre,
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 15,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                            decoration: BoxDecoration(
                              color: workshop.estaActivo
                                  ? Colors.green.withValues(alpha: 0.15)
                                  : Colors.red.withValues(alpha: 0.15),
                              borderRadius: BorderRadius.circular(20),
                            ),
                            child: Text(
                              workshop.estaActivo ? 'Activo' : 'Inactivo',
                              style: TextStyle(
                                color: workshop.estaActivo ? Colors.greenAccent : Colors.redAccent,
                                fontSize: 11,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          const Icon(Icons.location_on_outlined, color: Colors.white38, size: 13),
                          const SizedBox(width: 3),
                          Expanded(
                            child: Text(
                              workshop.direccion,
                              style: const TextStyle(color: Colors.white54, fontSize: 12),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ],
                      ),
                      if (workshop.especialidades != null && workshop.especialidades!.isNotEmpty) ...[
                        const SizedBox(height: 6),
                        Wrap(
                          spacing: 6,
                          children: workshop.especialidades!
                              .take(3)
                              .map((e) => _Chip(e))
                              .toList(),
                        ),
                      ],
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          const Icon(Icons.star, color: Colors.amber, size: 14),
                          const SizedBox(width: 3),
                          Text(
                            workshop.calificacionPromedio.toStringAsFixed(1),
                            style: const TextStyle(color: Colors.white54, fontSize: 12),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          // Acciones rápidas
          const Divider(color: Colors.white12, height: 1),
          Row(
            children: [
              Expanded(
                child: TextButton.icon(
                  onPressed: onRequests,
                  icon: const Icon(Icons.inbox, size: 16),
                  label: const Text('Solicitudes', style: TextStyle(fontSize: 12)),
                  style: TextButton.styleFrom(foregroundColor: const Color(0xFF0096FF)),
                ),
              ),
              const VerticalDivider(color: Colors.white12, width: 1),
              Expanded(
                child: TextButton.icon(
                  onPressed: onHistory,
                  icon: const Icon(Icons.history, size: 16),
                  label: const Text('Historial', style: TextStyle(fontSize: 12)),
                  style: TextButton.styleFrom(foregroundColor: Colors.white54),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _Chip extends StatelessWidget {
  final String label;
  const _Chip(this.label);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: const Color(0xFF0096FF).withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: const Color(0xFF0096FF).withValues(alpha: 0.4)),
      ),
      child: Text(label, style: const TextStyle(color: Color(0xFF0096FF), fontSize: 10)),
    );
  }
}
