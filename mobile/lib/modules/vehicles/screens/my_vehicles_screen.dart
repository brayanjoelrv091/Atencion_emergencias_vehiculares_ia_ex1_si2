/// CU06 — Gestión de Vehículos del usuario autenticado.
///
/// Permite listar, registrar y eliminar vehículos.
/// Endpoint: GET/POST/DELETE /me/vehicles
library;

import 'package:flutter/material.dart';

import '../../../core/api_client.dart';
import '../../auth/models/user_model.dart';
import '../../auth/services/auth_service.dart';

class MyVehiclesScreen extends StatefulWidget {
  const MyVehiclesScreen({super.key});

  @override
  State<MyVehiclesScreen> createState() => _MyVehiclesScreenState();
}

class _MyVehiclesScreenState extends State<MyVehiclesScreen> {
  List<Vehicle> _vehicles = [];
  bool _loading = true;
  String _error = '';

  // Controladores del formulario de nuevo vehículo
  final _marcaCtrl = TextEditingController();
  final _modeloCtrl = TextEditingController();
  final _placaCtrl = TextEditingController();
  final _anioCtrl = TextEditingController();
  final _colorCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadVehicles();
  }

  @override
  void dispose() {
    _marcaCtrl.dispose();
    _modeloCtrl.dispose();
    _placaCtrl.dispose();
    _anioCtrl.dispose();
    _colorCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadVehicles() async {
    setState(() {
      _loading = true;
      _error = '';
    });
    try {
      final profile = await AuthService.getMe();
      setState(() => _vehicles = profile.vehiculos);
    } on ApiException catch (e) {
      setState(() => _error = e.message);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _addVehicle() async {
    final marca = _marcaCtrl.text.trim();
    final modelo = _modeloCtrl.text.trim();
    final placa = _placaCtrl.text.trim();
    final anioStr = _anioCtrl.text.trim();
    final color = _colorCtrl.text.trim();

    if (marca.isEmpty || modelo.isEmpty || placa.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Marca, modelo y placa son obligatorios')),
      );
      return;
    }

    try {
      await AuthService.addVehicle(
        marca: marca,
        modelo: modelo,
        placa: placa,
        anio: anioStr.isNotEmpty ? int.tryParse(anioStr) : null,
        color: color.isNotEmpty ? color : null,
      );
      _marcaCtrl.clear();
      _modeloCtrl.clear();
      _placaCtrl.clear();
      _anioCtrl.clear();
      _colorCtrl.clear();
      if (mounted) Navigator.pop(context);
      await _loadVehicles();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('✅ Vehículo registrado'),
            backgroundColor: Color(0xFF00C853),
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

  Future<void> _deleteVehicle(int vehicleId, String placa) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF111629),
        title: const Text('Eliminar vehículo', style: TextStyle(color: Colors.white)),
        content: Text(
          '¿Eliminar el vehículo con placa $placa?',
          style: const TextStyle(color: Colors.white70),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancelar', style: TextStyle(color: Colors.white54)),
          ),
          TextButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Eliminar', style: TextStyle(color: Color(0xFFFF6B6B))),
          ),
        ],
      ),
    );
    if (confirm != true) return;
    try {
      await AuthService.deleteVehicle(vehicleId);
      await _loadVehicles();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Vehículo eliminado')),
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

  void _showAddDialog() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: const Color(0xFF111629),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => Padding(
        padding: EdgeInsets.only(
          left: 20,
          right: 20,
          top: 24,
          bottom: MediaQuery.of(ctx).viewInsets.bottom + 24,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Registrar Vehículo',
              style: TextStyle(
                color: Color(0xFF00F2FF),
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            _buildInput(_marcaCtrl, 'Marca *', 'Ej. Toyota'),
            const SizedBox(height: 12),
            _buildInput(_modeloCtrl, 'Modelo *', 'Ej. Corolla'),
            const SizedBox(height: 12),
            _buildInput(_placaCtrl, 'Placa *', 'Ej. ABC-123'),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(child: _buildInput(_anioCtrl, 'Año', '2020', numeric: true)),
                const SizedBox(width: 12),
                Expanded(child: _buildInput(_colorCtrl, 'Color', 'Rojo')),
              ],
            ),
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _addVehicle,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF00F2FF),
                  foregroundColor: Colors.black,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: const Text(
                  'REGISTRAR',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInput(
    TextEditingController ctrl,
    String label,
    String hint, {
    bool numeric = false,
  }) {
    return TextField(
      controller: ctrl,
      keyboardType: numeric ? TextInputType.number : TextInputType.text,
      style: const TextStyle(color: Colors.white),
      decoration: InputDecoration(
        labelText: label,
        labelStyle: const TextStyle(color: Colors.white54),
        hintText: hint,
        hintStyle: const TextStyle(color: Colors.white24),
        filled: true,
        fillColor: const Color(0xFF1A1F38),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: BorderSide.none,
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: Color(0xFF00F2FF)),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0E1A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF111629),
        title: const Text(
          'Mis Vehículos',
          style: TextStyle(color: Color(0xFF00F2FF), letterSpacing: 1),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Color(0xFF00F2FF)),
            onPressed: _loadVehicles,
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _showAddDialog,
        backgroundColor: const Color(0xFF00F2FF),
        foregroundColor: Colors.black,
        icon: const Icon(Icons.add),
        label: const Text('Agregar', style: TextStyle(fontWeight: FontWeight.bold)),
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_loading) {
      return const Center(child: CircularProgressIndicator(color: Color(0xFF00F2FF)));
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
              ElevatedButton(onPressed: _loadVehicles, child: const Text('Reintentar')),
            ],
          ),
        ),
      );
    }
    if (_vehicles.isEmpty) {
      return const Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.directions_car_outlined, color: Colors.white24, size: 64),
            SizedBox(height: 16),
            Text(
              'Sin vehículos registrados',
              style: TextStyle(color: Colors.white54, fontSize: 16),
            ),
            SizedBox(height: 8),
            Text(
              'Toca el botón + para agregar uno',
              style: TextStyle(color: Colors.white38, fontSize: 13),
            ),
          ],
        ),
      );
    }
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _vehicles.length,
      itemBuilder: (_, i) => _VehicleCard(
        vehicle: _vehicles[i],
        onDelete: () => _deleteVehicle(_vehicles[i].id, _vehicles[i].placa),
      ),
    );
  }
}

class _VehicleCard extends StatelessWidget {
  final Vehicle vehicle;
  final VoidCallback onDelete;

  const _VehicleCard({required this.vehicle, required this.onDelete});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF111629),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFF00F2FF).withValues(alpha: 0.2)),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: const Color(0xFF00F2FF).withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(10),
            ),
            child: const Icon(Icons.directions_car, color: Color(0xFF00F2FF), size: 28),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '${vehicle.marca} ${vehicle.modelo}',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 15,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Placa: ${vehicle.placa}',
                  style: const TextStyle(color: Color(0xFF00F2FF), fontSize: 13),
                ),
                if (vehicle.anio != null || vehicle.color != null)
                  Text(
                    [
                      if (vehicle.anio != null) '${vehicle.anio}',
                      if (vehicle.color != null) vehicle.color!,
                    ].join(' · '),
                    style: const TextStyle(color: Colors.white54, fontSize: 12),
                  ),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.delete_outline, color: Color(0xFFFF6B6B)),
            onPressed: onDelete,
          ),
        ],
      ),
    );
  }
}
