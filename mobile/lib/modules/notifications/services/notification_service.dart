/// CU16/CU17 — Servicio de Notificaciones en Tiempo Real.
///
/// Conecta al WebSocket ws://{base}/payments/ws/notifications/{user_id}
/// y propaga eventos a través de un Stream global.
library;

import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

import '../../../config.dart';

/// Modelo de notificación recibida por WS.
class AppNotification {
  final String titulo;
  final String mensaje;
  final String tipo;
  final DateTime timestamp;

  AppNotification({
    required this.titulo,
    required this.mensaje,
    required this.tipo,
    required this.timestamp,
  });

  factory AppNotification.fromJson(Map<String, dynamic> j) => AppNotification(
        titulo: j['titulo'] as String? ?? j['title'] as String? ?? 'Notificación',
        mensaje: j['mensaje'] as String? ?? j['message'] as String? ?? '',
        tipo: j['type'] as String? ?? 'notification',
        timestamp: j['timestamp'] != null
            ? DateTime.tryParse(j['timestamp'] as String) ?? DateTime.now()
            : DateTime.now(),
      );
}

/// Singleton que mantiene la conexión WS de notificaciones.
class NotificationService {
  NotificationService._();
  static final NotificationService instance = NotificationService._();

  WebSocketChannel? _channel;
  final StreamController<AppNotification> _controller =
      StreamController<AppNotification>.broadcast();

  /// Stream que emite notificaciones recibidas del backend.
  Stream<AppNotification> get notifications => _controller.stream;

  bool get isConnected => _channel != null;

  /// Conecta al canal de notificaciones para un usuario autenticado.
  void connect(int userId, String token) {
    if (_channel != null) return; // ya conectado
    final wsUrl =
        '${AppConfig.wsBaseUrl}/payments/ws/notifications/$userId?token=$token';
    debugPrint('[NotificationService] Conectando a $wsUrl');
    try {
      _channel = WebSocketChannel.connect(Uri.parse(wsUrl));
      _channel!.stream.listen(
        (raw) {
          try {
            final data = jsonDecode(raw as String) as Map<String, dynamic>;
            final notif = AppNotification.fromJson(data);
            _controller.add(notif);
            debugPrint('[NotificationService] 📲 ${notif.titulo}: ${notif.mensaje}');
          } catch (e) {
            debugPrint('[NotificationService] Parse error: $e');
          }
        },
        onError: (e) => debugPrint('[NotificationService] WS Error: $e'),
        onDone: () {
          debugPrint('[NotificationService] WS desconectado');
          _channel = null;
        },
        cancelOnError: false,
      );
    } catch (e) {
      debugPrint('[NotificationService] Conexión fallida: $e');
      _channel = null;
    }
  }

  void disconnect() {
    _channel?.sink.close();
    _channel = null;
  }

  void dispose() {
    disconnect();
    _controller.close();
  }
}
