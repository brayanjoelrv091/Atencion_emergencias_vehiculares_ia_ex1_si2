/// CU16/CU17 — Pantalla del Centro de Notificaciones.
///
/// Muestra el historial de notificaciones recibidas en la sesión actual.
/// Se alimenta del NotificationService (WebSocket).
library;

import 'dart:async';

import 'package:flutter/material.dart';

import '../services/notification_service.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  final List<AppNotification> _notifications = [];
  late final StreamSubscription<AppNotification> _sub;

  @override
  void initState() {
    super.initState();
    _sub = NotificationService.instance.notifications.listen((notif) {
      if (mounted) setState(() => _notifications.insert(0, notif));
    });
  }

  @override
  void dispose() {
    _sub.cancel();
    super.dispose();
  }

  void _clearAll() {
    setState(() => _notifications.clear());
  }

  Color _typeColor(String tipo) {
    return switch (tipo) {
      'payment_approved' => Colors.greenAccent,
      'notification' => const Color(0xFF00F2FF),
      'location_update' => Colors.purpleAccent,
      _ => Colors.blueAccent,
    };
  }

  IconData _typeIcon(String tipo) {
    return switch (tipo) {
      'payment_approved' => Icons.check_circle,
      'notification' => Icons.notifications,
      'location_update' => Icons.location_on,
      _ => Icons.info_outline,
    };
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0E1A),
      appBar: AppBar(
        backgroundColor: const Color(0xFF111629),
        title: Row(
          children: [
            const Text(
              'Notificaciones',
              style: TextStyle(color: Color(0xFF00F2FF), letterSpacing: 1),
            ),
            const SizedBox(width: 8),
            if (_notifications.isNotEmpty)
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
                decoration: BoxDecoration(
                  color: const Color(0xFF00F2FF),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  '${_notifications.length}',
                  style: const TextStyle(color: Colors.black, fontSize: 12, fontWeight: FontWeight.bold),
                ),
              ),
          ],
        ),
        actions: [
          if (_notifications.isNotEmpty)
            IconButton(
              icon: const Icon(Icons.clear_all, color: Colors.white54),
              onPressed: _clearAll,
              tooltip: 'Limpiar todo',
            ),
        ],
      ),
      body: _notifications.isEmpty
          ? _buildEmpty()
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _notifications.length,
              itemBuilder: (_, i) => _NotificationCard(
                notification: _notifications[i],
                typeColor: _typeColor(_notifications[i].tipo),
                typeIcon: _typeIcon(_notifications[i].tipo),
              ),
            ),
    );
  }

  Widget _buildEmpty() {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: const Color(0xFF111629),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.notifications_none,
              color: Colors.white24,
              size: 56,
            ),
          ),
          const SizedBox(height: 20),
          const Text(
            'Sin notificaciones',
            style: TextStyle(color: Colors.white54, fontSize: 16),
          ),
          const SizedBox(height: 8),
          const Text(
            'Recibirás alertas de pagos y\nactualizaciones en tiempo real',
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.white38, fontSize: 13),
          ),
        ],
      ),
    );
  }
}

class _NotificationCard extends StatelessWidget {
  final AppNotification notification;
  final Color typeColor;
  final IconData typeIcon;

  const _NotificationCard({
    required this.notification,
    required this.typeColor,
    required this.typeIcon,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF111629),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: typeColor.withValues(alpha: 0.25)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: typeColor.withValues(alpha: 0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(typeIcon, color: typeColor, size: 18),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  notification.titulo,
                  style: TextStyle(
                    color: typeColor,
                    fontWeight: FontWeight.w600,
                    fontSize: 14,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  notification.mensaje,
                  style: const TextStyle(color: Colors.white70, fontSize: 13),
                ),
                const SizedBox(height: 6),
                Text(
                  _formatTime(notification.timestamp),
                  style: const TextStyle(color: Colors.white38, fontSize: 11),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  String _formatTime(DateTime dt) {
    final now = DateTime.now();
    final diff = now.difference(dt);
    if (diff.inSeconds < 60) return 'Ahora mismo';
    if (diff.inMinutes < 60) return 'Hace ${diff.inMinutes} min';
    if (diff.inHours < 24) return 'Hace ${diff.inHours} h';
    return '${dt.day}/${dt.month} ${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';
  }
}
