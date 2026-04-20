/// main.dart — Entry point del monolito modular RutAIGeoProxi Mobile.
///
/// Rutas:
///   /              → Splash / Auth gate
///   /login         → Pantalla de login (CU1)
///   /home          → Dashboard principal
///   /incidents     → Mis incidentes (CU7 lista)
///   /report        → Reportar incidente (CU7)
///   /incident-detail → Ficha técnica (CU9)
///   /workshops     → Talleres (CU10-CU13)
library;

import 'package:flutter/material.dart';

import 'core/api_client.dart';
import 'modules/auth/screens/login_screen.dart';
import 'modules/auth/screens/register_screen.dart';
import 'modules/auth/screens/forgot_password_screen.dart';
import 'modules/incidents/screens/my_incidents_screen.dart';

void main() {
  runApp(const RutAIGeoProxiApp());
}

class RutAIGeoProxiApp extends StatelessWidget {
  const RutAIGeoProxiApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'RutAIGeoProxi',
      debugShowCheckedModeBanner: false,
      theme: _buildTheme(),
      home: const _AuthGate(),
      routes: {
        '/login': (_) => const _LoginWrapper(),
        '/register': (_) => const RegisterScreen(),
        '/forgot-password': (_) => const ForgotPasswordScreen(),
        '/home':  (_) => const _HomeWrapper(),
        '/incidents': (_) => const MyIncidentsScreen(),
        '/report': (_) => const _ReportIncidentPlaceholder(),
        '/incident-detail': (_) => const _IncidentDetailPlaceholder(),
        '/workshops': (_) => const _WorkshopsPlaceholder(),
      },

    );
  }

  ThemeData _buildTheme() {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      colorScheme: ColorScheme.dark(
        primary: const Color(0xFF00F2FF),
        secondary: const Color(0xFF0096FF),
        surface: const Color(0xFF111629),
        error: const Color(0xFFFF6B6B),
      ),
      scaffoldBackgroundColor: const Color(0xFF0A0E1A),
      fontFamily: 'Roboto',
      appBarTheme: const AppBarTheme(
        backgroundColor: Color(0xFF111629),
        foregroundColor: Color(0xFF00F2FF),
        elevation: 0,
        titleTextStyle: TextStyle(
          color: Color(0xFF00F2FF),
          fontSize: 18,
          letterSpacing: 1,
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: const Color(0xFF00F2FF),
          foregroundColor: Colors.black,
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
      ),
    );
  }
}

// ── Auth Gate ──────────────────────────────────────────────────────────

class _AuthGate extends StatefulWidget {
  const _AuthGate();

  @override
  State<_AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<_AuthGate> {
  @override
  void initState() {
    super.initState();
    _check();
  }

  Future<void> _check() async {
    await Future.delayed(const Duration(milliseconds: 300));
    if (!mounted) return;
    final token = await ApiClient.getToken();
    if (token != null && token.isNotEmpty) {
      Navigator.pushReplacementNamed(context, '/home');
    } else {
      Navigator.pushReplacementNamed(context, '/login');
    }
  }

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      backgroundColor: Color(0xFF0A0E1A),
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.car_repair, size: 64, color: Color(0xFF00F2FF)),
            SizedBox(height: 16),
            Text(
              'RutAIGeoProxi',
              style: TextStyle(
                color: Color(0xFF00F2FF),
                fontSize: 24,
                fontWeight: FontWeight.bold,
                letterSpacing: 3,
              ),
            ),
            SizedBox(height: 24),
            CircularProgressIndicator(color: Color(0xFF00F2FF)),
          ],
        ),
      ),
    );
  }
}

// ── Wrappers ───────────────────────────────────────────────────────────

class _LoginWrapper extends StatelessWidget {
  const _LoginWrapper();

  @override
  Widget build(BuildContext context) {
    return LoginScreen(
      onLoginSuccess: () =>
          Navigator.pushReplacementNamed(context, '/home'),
    );
  }
}

class _HomeWrapper extends StatelessWidget {
  const _HomeWrapper();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0E1A),
      appBar: AppBar(
        title: const Text('RutAIGeoProxi'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              await ApiClient.clearToken();
              if (context.mounted) {
                Navigator.pushReplacementNamed(context, '/login');
              }
            },
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              '¿Qué deseas hacer?',
              style: TextStyle(color: Colors.white70, fontSize: 16),
            ),
            const SizedBox(height: 20),
            _HomeButton(
              icon: Icons.warning_amber_rounded,
              label: 'Mis Incidentes',
              sub: 'CU7 · CU9 · CU14',
              color: const Color(0xFF00F2FF),
              onTap: () => Navigator.pushNamed(context, '/incidents'),
            ),
            const SizedBox(height: 12),
            _HomeButton(
              icon: Icons.store,
              label: 'Talleres',
              sub: 'CU10 · CU11 · CU12 · CU13',
              color: const Color(0xFF0096FF),
              onTap: () => Navigator.pushNamed(context, '/workshops'),
            ),
            const SizedBox(height: 12),
            _HomeButton(
              icon: Icons.add_alert,
              label: 'Reportar Incidente',
              sub: 'CU7 · GPS + Fotos + Audio',
              color: const Color(0xFFFF6B6B),
              onTap: () => Navigator.pushNamed(context, '/report'),
            ),
          ],
        ),
      ),
    );
  }
}

class _HomeButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final String sub;
  final Color color;
  final VoidCallback onTap;

  const _HomeButton({
    required this.icon,
    required this.label,
    required this.sub,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          color: const Color(0xFF111629),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: color.withOpacity(0.3)),
        ),
        child: Row(
          children: [
            Icon(icon, color: color, size: 32),
            const SizedBox(width: 16),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(label,
                    style: const TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.w600)),
                Text(sub,
                    style: TextStyle(color: color.withOpacity(0.7), fontSize: 12)),
              ],
            ),
            const Spacer(),
            Icon(Icons.chevron_right, color: color.withOpacity(0.5)),
          ],
        ),
      ),
    );
  }
}

// ── Placeholders de pantallas pendientes ──────────────────────────────

class _ReportIncidentPlaceholder extends StatelessWidget {
  const _ReportIncidentPlaceholder();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Reportar Incidente (CU7)')),
      body: const Center(
          child: Text('Pantalla de reporte — implementar en siguiente sprint',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.white54))),
    );
  }
}

class _IncidentDetailPlaceholder extends StatelessWidget {
  const _IncidentDetailPlaceholder();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Ficha Técnica (CU9)')),
      body: const Center(
          child: Text('Ficha técnica — implementar en siguiente sprint',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.white54))),
    );
  }
}

class _WorkshopsPlaceholder extends StatelessWidget {
  const _WorkshopsPlaceholder();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Talleres (CU10-CU13)')),
      body: const Center(
          child: Text('Pantallas de talleres — implementar en siguiente sprint',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.white54))),
    );
  }
}
