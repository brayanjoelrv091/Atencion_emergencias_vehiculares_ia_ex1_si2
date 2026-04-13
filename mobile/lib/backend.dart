import 'dart:convert';

import 'package:http/http.dart' as http;

import 'config.dart';
import 'session.dart';

class Backend {
  static Uri _uri(String path) => Uri.parse('${apiBaseUrl()}$path');

  static Future<Map<String, String>> _headers({bool jsonBody = false, bool withAuth = true}) async {
    final h = <String, String>{};
    if (jsonBody) h['Content-Type'] = 'application/json';
    if (withAuth) {
      final t = await Session.getToken();
      if (t != null) h['Authorization'] = 'Bearer $t';
    }
    return h;
  }

  static Future<String?> login(String email, String password) async {
    final r = await http.post(
      _uri('/auth/login'),
      headers: await _headers(jsonBody: true, withAuth: false),
      body: jsonEncode({'email': email, 'password': password}),
    );
    if (r.statusCode != 200) return r.body;
    final m = jsonDecode(r.body) as Map<String, dynamic>;
    final token = m['access_token'] as String?;
    if (token != null) await Session.setToken(token);
    return null;
  }

  static Future<String?> register(String name, String email, String password) async {
    final r = await http.post(
      _uri('/auth/register'),
      headers: await _headers(jsonBody: true, withAuth: false),
      body: jsonEncode({'name': name, 'email': email, 'password': password}),
    );
    if (r.statusCode == 201) return null;
    try {
      final e = jsonDecode(r.body);
      if (e is Map && e['detail'] != null) return e['detail'].toString();
    } catch (_) {}
    return 'Error ${r.statusCode}';
  }

  static Future<void> logout() async {
    final t = await Session.getToken();
    if (t == null) return;
    await http.post(_uri('/auth/logout'), headers: await _headers());
    await Session.setToken(null);
  }

  static Future<Map<String, dynamic>?> me() async {
    final r = await http.get(_uri('/me'), headers: await _headers());
    if (r.statusCode != 200) return null;
    return jsonDecode(r.body) as Map<String, dynamic>;
  }

  static Future<String?> addVehicle({
    required String brand,
    required String model,
    required String licensePlate,
    int? year,
  }) async {
    final body = <String, dynamic>{
      'brand': brand,
      'model': model,
      'license_plate': licensePlate,
    };
    if (year != null) body['year'] = year;
    final r = await http.post(
      _uri('/me/vehicles'),
      headers: await _headers(jsonBody: true),
      body: jsonEncode(body),
    );
    if (r.statusCode == 201) return null;
    try {
      final e = jsonDecode(r.body);
      if (e is Map && e['detail'] != null) return e['detail'].toString();
    } catch (_) {}
    return 'Error ${r.statusCode}';
  }

  static Future<void> deleteVehicle(int id) async {
    await http.delete(_uri('/me/vehicles/$id'), headers: await _headers());
  }

  // CU-04: Recuperar contraseña
  static Future<String?> forgotPassword(String email) async {
    final r = await http.post(
      _uri('/auth/forgot-password'),
      headers: await _headers(jsonBody: true, withAuth: false),
      body: jsonEncode({'email': email}),
    );
    if (r.statusCode == 200) {
      final m = jsonDecode(r.body) as Map<String, dynamic>;
      // Si hay debug_token en la respuesta, el UI puede mostrarlo para pruebas
      return m['debug_token']?.toString() ?? 'OK';
    }
    try {
      final e = jsonDecode(r.body);
      if (e is Map && e['detail'] != null) return e['detail'].toString();
    } catch (_) {}
    return 'Error ${r.statusCode}';
  }

  static Future<String?> resetPassword(String token, String newPassword) async {
    final r = await http.post(
      _uri('/auth/reset-password'),
      headers: await _headers(jsonBody: true, withAuth: false),
      body: jsonEncode({'token': token, 'new_password': newPassword}),
    );
    if (r.statusCode == 204) return null;
    try {
      final e = jsonDecode(r.body);
      if (e is Map && e['detail'] != null) return e['detail'].toString();
    } catch (_) {}
    return 'Error ${r.statusCode}';
  }
}
