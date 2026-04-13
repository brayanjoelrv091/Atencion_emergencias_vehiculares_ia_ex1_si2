import 'package:flutter/material.dart';
import '../backend.dart';

class ResetPasswordScreen extends StatefulWidget {
  final String? token;
  const ResetPasswordScreen({super.key, this.token});

  @override
  State<ResetPasswordScreen> createState() => _ResetPasswordScreenState();
}

class _ResetPasswordScreenState extends State<ResetPasswordScreen> {
  late final _tokenController = TextEditingController(text: widget.token);
  final _passwordController = TextEditingController();
  final _confirmController = TextEditingController();
  bool _loading = false;
  String? _error;

  void _submit() async {
    final token = _tokenController.text.trim();
    final pass = _passwordController.text.trim();
    final confirm = _confirmController.text.trim();

    if (token.isEmpty || pass.isEmpty) return;
    if (pass != confirm) {
      setState(() => _error = 'Las contraseñas no coinciden');
      return;
    }
    if (pass.length < 8) {
      setState(() => _error = 'Mínimo 8 caracteres');
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
    });

    final res = await Backend.resetPassword(token, pass);
    if (res == null) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Contraseña actualizada. Inicia sesión.')),
        );
        Navigator.popUntil(context, (route) => route.isFirst);
      }
    } else {
      setState(() {
        _loading = false;
        _error = res;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Nueva Contraseña')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          children: [
            TextField(
              controller: _tokenController,
              decoration: const InputDecoration(
                labelText: 'Token de Recuperación',
                border: OutlineInputBorder(),
              ),
              enabled: !_loading,
            ),
            const SizedBox(height: 20),
            TextField(
              controller: _passwordController,
              decoration: const InputDecoration(
                labelText: 'Nueva Contraseña',
                border: OutlineInputBorder(),
              ),
              obscureText: true,
              enabled: !_loading,
            ),
            const SizedBox(height: 20),
            TextField(
              controller: _confirmController,
              decoration: const InputDecoration(
                labelText: 'Confirmar Contraseña',
                border: OutlineInputBorder(),
              ),
              obscureText: true,
              enabled: !_loading,
            ),
            const SizedBox(height: 20),
            if (_error != null) ...[
              Text(_error!, style: const TextStyle(color: Colors.red)),
              const SizedBox(height: 10),
            ],
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                onPressed: _loading ? null : _submit,
                child: _loading
                    ? const CircularProgressIndicator()
                    : const Text('Actualizar Contraseña'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
