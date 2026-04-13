import 'package:flutter/material.dart';

import 'backend.dart';
import 'screens/home_screen.dart';
import 'screens/login_screen.dart';
import 'session.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final t = await Session.getToken();
  runApp(RutaiApp(initialLoggedIn: t != null && t.isNotEmpty));
}

class RutaiApp extends StatefulWidget {
  const RutaiApp({super.key, required this.initialLoggedIn});

  final bool initialLoggedIn;

  @override
  State<RutaiApp> createState() => _RutaiAppState();
}

class _RutaiAppState extends State<RutaiApp> {
  late bool _loggedIn = widget.initialLoggedIn;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'RutAIGeoProxi',
      theme: ThemeData(colorSchemeSeed: Colors.indigo, useMaterial3: true),
      home: _loggedIn
          ? HomeScreen(
              onLogout: () async {
                await Backend.logout();
                if (mounted) setState(() => _loggedIn = false);
              },
            )
          : LoginScreen(
              onLoggedIn: () {
                setState(() => _loggedIn = true);
              },
            ),
    );
  }
}
