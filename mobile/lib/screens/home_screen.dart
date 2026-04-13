import 'package:flutter/material.dart';

import '../backend.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key, required this.onLogout});

  final Future<void> Function() onLogout;

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  Map<String, dynamic>? _me;
  String? _error;
  bool _loading = true;

  final _brand = TextEditingController();
  final _model = TextEditingController();
  final _plate = TextEditingController();
  final _year = TextEditingController();
  String? _vehErr;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _brand.dispose();
    _model.dispose();
    _plate.dispose();
    _year.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    final m = await Backend.me();
    if (!mounted) return;
    setState(() {
      _me = m;
      _loading = false;
      if (m == null) _error = 'No se pudo cargar el perfil.';
    });
  }

  Future<void> _addVehicle() async {
    final role = _me?['role'] as String?;
    if (role != 'cliente') {
      setState(() => _vehErr = 'Solo rol cliente puede gestionar vehículos.');
      return;
    }
    setState(() => _vehErr = null);
    final y = int.tryParse(_year.text.trim());
    final err = await Backend.addVehicle(
      brand: _brand.text.trim(),
      model: _model.text.trim(),
      licensePlate: _plate.text.trim(),
      year: y,
    );
    if (!mounted) return;
    if (err != null) {
      setState(() => _vehErr = err);
    } else {
      _brand.clear();
      _model.clear();
      _plate.clear();
      _year.clear();
      await _load();
    }
  }

  Future<void> _delete(int id) async {
    await Backend.deleteVehicle(id);
    await _load();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Inicio'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              await widget.onLogout();
            },
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                if (_error != null) Text(_error!, style: const TextStyle(color: Colors.red)),
                if (_me != null) ...[
                  Text('${_me!['name']}', style: Theme.of(context).textTheme.titleLarge),
                  Text('${_me!['email']}'),
                  Text('Rol: ${_me!['role']}'),
                  const SizedBox(height: 16),
                  if (_me!['role'] == 'cliente') ...[
                    const Text('Vehículos', style: TextStyle(fontWeight: FontWeight.bold)),
                    ..._vehicles(),
                    const SizedBox(height: 12),
                    const Text('Nuevo vehículo'),
                    TextField(controller: _brand, decoration: const InputDecoration(labelText: 'Marca')),
                    TextField(controller: _model, decoration: const InputDecoration(labelText: 'Modelo')),
                    TextField(controller: _plate, decoration: const InputDecoration(labelText: 'Placa')),
                    TextField(controller: _year, decoration: const InputDecoration(labelText: 'Año (opcional)'), keyboardType: TextInputType.number),
                    if (_vehErr != null) Text(_vehErr!, style: const TextStyle(color: Colors.red)),
                    FilledButton(onPressed: _addVehicle, child: const Text('Guardar')),
                  ] else
                    const Text('En Ciclo 1 los vehículos en API son solo para rol cliente.', style: TextStyle(color: Colors.black54)),
                ],
              ],
            ),
    );
  }

  List<Widget> _vehicles() {
    final list = _me!['vehicles'];
    if (list is! List || list.isEmpty) {
      return [const Text('Sin vehículos.')];
    }
    return list.map<Widget>((v) {
      final m = v as Map<String, dynamic>;
      final id = m['id'] as int;
      return ListTile(
        title: Text('${m['brand']} ${m['model']}'),
        subtitle: Text('${m['license_plate']}'),
        trailing: IconButton(icon: const Icon(Icons.delete_outline), onPressed: () => _delete(id)),
      );
    }).toList();
  }
}
