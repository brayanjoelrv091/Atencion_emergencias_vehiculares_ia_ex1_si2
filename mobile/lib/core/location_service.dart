import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:geolocator/geolocator.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:rutaigeoproxi_mobile/config.dart';

class LocationTrackingService {
    WebSocketChannel? _channel;
    
    /// Conecta al WebSocket de tracking para un incidente (CU15).
    void connectTracking(int incidentId) {
        _channel = WebSocketChannel.connect(
            Uri.parse('${AppConfig.wsBaseUrl}/assignments/ws/track/$incidentId'),
        );
    }
    
    /// Inicia el envío de coordenadas GPS en tiempo real (CU15).
    void startSendingLocation(String role) async {
        // Verificar permisos
        LocationPermission permission = await Geolocator.checkPermission();
        if (permission == LocationPermission.denied) {
            permission = await Geolocator.requestPermission();
        }
        
        if (permission == LocationPermission.whileInUse || permission == LocationPermission.always) {
            Geolocator.getPositionStream(
                locationSettings: const LocationSettings(
                    accuracy: LocationAccuracy.high,
                    distanceFilter: 10,
                ),
            ).listen((Position position) {
                if (_channel != null) {
                    final data = {
                        "lat": position.latitude,
                        "lng": position.longitude,
                        "role": role,
                        "timestamp": DateTime.now().toIso8601String(),
                    };
                    _channel!.sink.add(jsonEncode(data));
                    debugPrint("Enviando GPS: ${position.latitude}, ${position.longitude}");
                }
            });
        }
    }
    
    /// Escucha actualizaciones de otros actores (CU17).
    Stream<dynamic>? get locationStream => _channel?.stream.map((event) => jsonDecode(event));
    
    void stopTracking() {
        _channel?.sink.close();
    }
}
