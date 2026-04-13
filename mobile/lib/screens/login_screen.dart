import 'package:flutter/material.dart';

import '../backend.dart';
import 'forgot_password_screen.dart';
import 'register_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key, required this.onLoggedIn});

  final VoidCallback onLoggedIn;

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _email = TextEditingController();
  final _password = TextEditingController();
  String? _error;
  bool _loading = false;

  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    setState(() {
      _error = null;
      _loading = true;
    });
    final err = await Backend.login(_email.text.trim(), _password.text);
    if (!mounted) return;
    setState(() => _loading = false);
    if (err == null) {
      widget.onLoggedIn();
    } else {
      setState(() => _error = err.length > 120 ? 'Credenciales incorrectas.' : err);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('RutAIGeoProxi — Login')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const Text('Ciclo 1: inicio de sesión (cliente)', style: TextStyle(color: Colors.black54)),
          const SizedBox(height: 16),
          TextField(
            controller: _email,
            decoration: const InputDecoration(labelText: 'Correo'),
            keyboardType: TextInputType.emailAddress,
            autocorrect: false,
          ),
          TextField(
            controller: _password,
            decoration: const InputDecoration(labelText: 'Contraseña'),
            obscureText: true,
          ),
          if (_error != null) ...[
            const SizedBox(height: 8),
            Text(_error!, style: const TextStyle(color: Colors.red)),
          ],
          const SizedBox(height: 16),
          FilledButton(
            onPressed: _loading ? null : _submit,
            child: Text(_loading ? 'Entrando…' : 'Entrar'),
          ),
          TextButton(
            onPressed: _loading
                ? null
                : () {
                    Navigator.of(context).push(MaterialPageRoute<void>(builder: (_) => const RegisterScreen()));
                  },
            child: const Text('Crear cuenta'),
          ),
          TextButton(
            onPressed: _loading
                ? null
                : () {
                    Navigator.of(context).push(MaterialPageRoute<void>(builder: (_) => const ForgotPasswordScreen()));
                  },
            child: const Text('Olvidé mi contraseña'),
          ),
        ],
      ),
    );
  }
}
