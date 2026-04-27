/// CU13 — Historial de atenciones del taller.
///
/// GET /workshops/{id}/history → lista historial completo (atendidos/cancelados).
library;

import 'package:flutter/material.dart';

import '../../../core/api_client.dart';
import '../models/workshop_model.dart';
import '../services/workshop_service.dart';

class WorkshopHistoryScreen extends StatefulWidget {
  final Workshop workshop;

  const WorkshopHistoryScreen({super.key, required this.workshop});

  @override
  State<WorkshopHistoryScreen> createState() => _WorkshopHistoryScreenState();
}

class _WorkshopHistoryScreenState extends State<WorkshopHistoryScreen> {
  List<ServiceHistory> _history = [];
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
      final list = await WorkshopService.getHistory(widget.workshop.id);
      setState(() => _history = list);
    } on ApiException catch (e) {
      setState(() => _error = e.message);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Color _statusColor(String estado) {
    return switch (estado) {
      'atendido' => Colors.greenAccent,
      'cancelado' => Colors.redAccent,
      'proceso' => Colors.blue,
      _ => Colors.orange,
    };
  }

  IconData _statusIcon(String estado) {
    return switch (estado) {
      'atendido' => Icons.check_circle,
      'cancelado' => Icons.cancel,
      'proceso' => Icons.sync,
      _ => Icons.hourglass_empty,
    };
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0E1A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF111629),
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Historial', style: TextStyle(color: Colors.white70, fontSize: 16)),
            Text(
              widget.workshop.nombre,
              style: const TextStyle(color: Colors.white38, fontSize: 12),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.white54),
            onPressed: _load,
          ),
        ],
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
    if (_history.isEmpty) {
      return const Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.history_outlined, color: Colors.white24, size: 64),
            SizedBox(height: 16),
            Text('Sin historial de atenciones', style: TextStyle(color: Colors.white54, fontSize: 16)),
          ],
        ),
      );
    }
    return RefreshIndicator(
      onRefresh: _load,
      color: const Color(0xFF0096FF),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _history.length,
        itemBuilder: (_, i) {
          final item = _history[i];
          final color = _statusColor(item.estado);
          return Container(
            margin: const EdgeInsets.only(bottom: 10),
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: const Color(0xFF111629),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: color.withValues(alpha: 0.2)),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: color.withValues(alpha: 0.1),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(_statusIcon(item.estado), color: color, size: 18),
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
                              item.tituloIncidente ?? 'Incidente #${item.incidenteId}',
                              style: const TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.w600,
                                fontSize: 14,
                              ),
                            ),
                          ),
                          Text(
                            item.estado,
                            style: TextStyle(color: color, fontSize: 12),
                          ),
                        ],
                      ),
                      const SizedBox(height: 4),
                      if (item.categoriaIncidente != null || item.severidadIncidente != null)
                        Row(
                          children: [
                            if (item.categoriaIncidente != null)
                              Text(
                                item.categoriaIncidente!,
                                style: const TextStyle(color: Colors.blue, fontSize: 11),
                              ),
                            if (item.categoriaIncidente != null && item.severidadIncidente != null)
                              const Text(' · ', style: TextStyle(color: Colors.white38)),
                            if (item.severidadIncidente != null)
                              Text(
                                item.severidadIncidente!,
                                style: const TextStyle(color: Colors.orange, fontSize: 11),
                              ),
                          ],
                        ),
                      if (item.notas != null) ...[
                        const SizedBox(height: 4),
                        Text(
                          item.notas!,
                          style: const TextStyle(color: Colors.white38, fontSize: 11),
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                      const SizedBox(height: 4),
                      Text(
                        _formatDate(item.actualizadoEn ?? item.creadoEn),
                        style: const TextStyle(color: Colors.white24, fontSize: 11),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  String _formatDate(String raw) {
    try {
      return raw.substring(0, 16).replaceAll('T', ' ');
    } catch (_) {
      return raw;
    }
  }
}
