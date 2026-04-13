import 'dart:io';

/// API FastAPI local. Emulador Android:10.0.2.2 = máquina host.
/// En dispositivo físico usa la IP LAN de tu PC (ej. http://192.168.1.10:8000).
String apiBaseUrl() {
  if (Platform.isAndroid) {
    return 'http://10.0.2.2:8000';
  }
  return 'http://127.0.0.1:8000';
}
