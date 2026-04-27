/// CU11/CU12 — Solicitudes de servicio del taller y cambio de estado.
///
/// GET /workshops/{id}/requests  → lista solicitudes pendientes
/// PATCH /workshops/requests/{id}/status  → actualiza estado
library;

import 'package:flutter/material.dart';

import '../../../core/api_client.dart';
import '../models/workshop_model.dart';
import '../services/workshop_service.dart';

class WorkshopRequestsScreen extends StatefulWidget {
  final Workshop workshop;

  const WorkshopRequestsScreen({super.key, required this.workshop});

  @override
  State<WorkshopRequestsScreen> createState() => _WorkshopRequestsScreenState();
}

class _WorkshopRequestsScreenState extends State<WorkshopRequestsScreen> {
  List<ServiceRequest> _requests = [];
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
      final list = await WorkshopService.listPendingRequests(widget.workshop.id);
      setState(() => _requests = list);
    } on ApiException catch (e) {
      setState(() => _error = e.message);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _updateStatus(ServiceRequest req, String nuevoEstado) async {
    try {
      await WorkshopService.updateStatus(req.id, nuevoEstado);
      await _load();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Estado actualizado → $nuevoEstado'),
            backgroundColor: const Color(0xFF00C853),
          ),
        );
      }
    } on ApiException catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: ${e.message}')),
        );
      }
    }
  }

  void _showStatusDialog(ServiceRequest req) {
    final transitions = _nextStates(req.estado);
    if (transitions.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Este estado no tiene transiciones posibles')),
      );
      return;
    }
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF111629),
        title: const Text('Cambiar Estado', style: TextStyle(color: Colors.white)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: transitions
              .map((state) => ListTile(
                    title: Text(state, style: const TextStyle(color: Colors.white)),
                    leading: Icon(_statusIcon(state), color: _statusColor(state)),
                    onTap: () {
                      Navigator.pop(ctx);
                      _updateStatus(req, state);
                    },
                  ))
              .toList(),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancelar', style: TextStyle(color: Colors.white54)),
          ),
        ],
      ),
    );
  }

  List<String> _nextStates(String current) {
    return switch (current) {
      'pendiente' => ['proceso', 'cancelado'],
      'proceso' => ['atendido', 'cancelado'],
      _ => [],
    };
  }

  Color _statusColor(String estado) {
    return switch (estado) {
      'pendiente' => Colors.orange,
      'proceso' => Colors.blue,
      'atendido' => Colors.green,
      'cancelado' => Colors.red,
      _ => Colors.grey,
    };
  }

  IconData _statusIcon(String estado) {
    return switch (estado) {
      'pendiente' => Icons.hourglass_empty,
      'proceso' => Icons.sync,
      'atendido' => Icons.check_circle,
      'cancelado' => Icons.cancel,
      _ => Icons.help_outline,
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
            const Text('Solicitudes', style: TextStyle(color: Color(0xFF0096FF), fontSize: 16)),
            Text(
              widget.workshop.nombre,
              style: const TextStyle(color: Colors.white54, fontSize: 12),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Color(0xFF0096FF)),
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
    if (_requests.isEmpty) {
      return const Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.inbox_outlined, color: Colors.white24, size: 64),
            SizedBox(height: 16),
            Text('Sin solicitudes pendientes', style: TextStyle(color: Colors.white54, fontSize: 16)),
          ],
        ),
      );
    }
    return RefreshIndicator(
      onRefresh: _load,
      color: const Color(0xFF0096FF),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _requests.length,
        itemBuilder: (_, i) => _RequestCard(
          request: _requests[i],
          statusColor: _statusColor(_requests[i].estado),
          statusIcon: _statusIcon(_requests[i].estado),
          onChangeStatus: () => _showStatusDialog(_requests[i]),
        ),
      ),
    );
  }
}

class _RequestCard extends StatelessWidget {
  final ServiceRequest request;
  final Color statusColor;
  final IconData statusIcon;
  final VoidCallback onChangeStatus;

  const _RequestCard({
    required this.request,
    required this.statusColor,
    required this.statusIcon,
    required this.onChangeStatus,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF111629),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: statusColor.withValues(alpha: 0.25)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(statusIcon, color: statusColor, size: 20),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Solicitud #${request.id} · Incidente #${request.incidenteId}',
                  style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600),
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: statusColor.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  request.estado,
                  style: TextStyle(color: statusColor, fontSize: 11),
                ),
              ),
            ],
          ),
          if (request.tituloIncidente != null) ...[
            const SizedBox(height: 8),
            Text(
              request.tituloIncidente!,
              style: const TextStyle(color: Colors.white70, fontSize: 13),
            ),
          ],
          if (request.severidadIncidente != null || request.categoriaIncidente != null) ...[
            const SizedBox(height: 6),
            Row(
              children: [
                if (request.categoriaIncidente != null)
                  _Tag(request.categoriaIncidente!, Colors.blue),
                const SizedBox(width: 6),
                if (request.severidadIncidente != null)
                  _Tag(request.severidadIncidente!, _severityColor(request.severidadIncidente!)),
              ],
            ),
          ],
          if (request.notas != null) ...[
            const SizedBox(height: 6),
            Text(
              'Notas: ${request.notas}',
              style: const TextStyle(color: Colors.white38, fontSize: 12),
            ),
          ],
          const SizedBox(height: 10),
          const Divider(color: Colors.white12, height: 1),
          const SizedBox(height: 6),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: onChangeStatus,
              icon: const Icon(Icons.swap_horiz, size: 16),
              label: const Text('Cambiar Estado', style: TextStyle(fontSize: 12)),
              style: OutlinedButton.styleFrom(
                foregroundColor: const Color(0xFF0096FF),
                side: const BorderSide(color: Color(0xFF0096FF)),
                padding: const EdgeInsets.symmetric(vertical: 6),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Color _severityColor(String sev) {
    return switch (sev) {
      'leve' => Colors.green,
      'moderado' => Colors.orange,
      'grave' => Colors.red,
      'critico' => const Color(0xFFFF1744),
      _ => Colors.grey,
    };
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
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: color.withValues(alpha: 0.4)),
      ),
      child: Text(text, style: TextStyle(color: color, fontSize: 10)),
    );
  }
}
