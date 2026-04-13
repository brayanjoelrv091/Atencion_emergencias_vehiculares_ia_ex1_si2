import 'package:flutter/material.dart';
import '../backend.dart';
import 'reset_password_screen.dart';

class ForgotPasswordScreen extends StatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  State<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  final _emailController = TextEditingController();
  bool _loading = false;
  String? _message;
  String? _debugToken;

  void _submit() async {
    if (_emailController.text.trim().isEmpty) return;
    setState(() {
      _loading = true;
      _message = null;
      _debugToken = null;
    });

    final res = await Backend.forgotPassword(_emailController.text.trim());
    setState(() {
      _loading = false;
      if (res == null || res.startsWith('Error')) {
        _message = 'Error: ${res ?? "No se pudo procesar"}';
      } else {
        _message = 'Si el correo existe, recibirás instrucciones.';
        if (res != 'OK') {
          _debugToken = res;
        }
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Recuperar Contraseña')),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          children: [
            const Text(
              'Ingresa tu email para recibir un token de recuperación.',
              style: TextStyle(fontSize: 16),
            ),
            const SizedBox(height: 20),
            TextField(
              controller: _emailController,
              decoration: const InputDecoration(
                labelText: 'Email',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.emailAddress,
              enabled: !_loading,
            ),
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                onPressed: _loading ? null : _submit,
                child: _loading
                    ? const CircularProgressIndicator()
                    : const Text('Enviar Instrucciones'),
              ),
            ),
            if (_message != null) ...[
              const SizedBox(height: 20),
              Text(
                _message!,
                style: TextStyle(
                  color: _message!.startsWith('Error') ? Colors.red : Colors.green,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
            if (_debugToken != null) ...[
              const SizedBox(height: 30),
              Container(
                padding: const EdgeInsets.all(12),
                color: Colors.orange.shade50,
                child: Column(
                  children: [
                    const Text('DEPURACIÓN: Token generado:', style: TextStyle(fontWeight: FontWeight.bold)),
                    SelectableText(_debugToken!, style: const TextStyle(fontFamily: 'monospace')),
                    TextButton(
                      onPressed: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(builder: (_) => ResetPasswordScreen(token: _debugToken)),
                        );
                      },
                      child: const Text('Ir a restablecer con este token'),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
