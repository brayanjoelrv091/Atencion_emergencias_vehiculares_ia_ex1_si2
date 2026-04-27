/// Cliente HTTP centralizado para el monolito modular RutAIGeoProxi.
///
/// Maneja:
///   - Inyección automática del JWT en headers
///   - Deserialización de errores del backend FastAPI
///   - Base URL configurable por entorno
library;

import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import '../config.dart';

class ApiException implements Exception {
  final int statusCode;
  final String message;

  const ApiException({required this.statusCode, required this.message});

  @override
  String toString() => 'ApiException($statusCode): $message';
}

class ApiClient {
  // ── URL base ────────────────────────────────────────────────────────
  // Ajusta según tu entorno:
  //   Android emulator → 10.0.2.2
  //   iOS simulator / web → localhost
  //   Dispositivo físico → IP de tu máquina en la red local
  static String get baseUrl => AppConfig.baseUrl;

  static const String _tokenKey = 'access_token';

  // ── Token ───────────────────────────────────────────────────────────

  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }

  static Future<void> saveToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
  }

  static Future<void> clearToken() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
  }

  // ── Headers ─────────────────────────────────────────────────────────

  static Future<Map<String, String>> _headers({
    bool auth = true,
    bool json = true,
  }) async {
    final headers = <String, String>{};
    if (json) headers['Content-Type'] = 'application/json';
    if (auth) {
      final token = await getToken();
      if (token != null) headers['Authorization'] = 'Bearer $token';
    }
    return headers;
  }

  // ── Manejo de errores ───────────────────────────────────────────────

  static ApiException _parseError(http.Response res) {
    try {
      final body = json.decode(res.body) as Map<String, dynamic>;
      final detail = body['detail'];
      final message = detail is String
          ? detail
          : detail.toString();
      return ApiException(statusCode: res.statusCode, message: message);
    } catch (_) {
      return ApiException(
        statusCode: res.statusCode,
        message: 'Error HTTP ${res.statusCode}',
      );
    }
  }

  static T _handleResponse<T>(
    http.Response res,
    T Function(dynamic json) fromJson,
  ) {
    if (res.statusCode >= 200 && res.statusCode < 300) {
      if (res.statusCode == 204 || res.body.isEmpty) {
        return fromJson(null);
      }
      return fromJson(json.decode(res.body));
    }
    throw _parseError(res);
  }

  // ── HTTP Methods ────────────────────────────────────────────────────

  static Future<T> get<T>(
    String path, {
    T Function(dynamic)? fromJson,
    bool auth = true,
  }) async {
    final res = await http.get(
      Uri.parse('$baseUrl$path'),
      headers: await _headers(auth: auth),
    );
    return _handleResponse(res, fromJson ?? (j) => j as T);
  }

  static Future<T> post<T>(
    String path, {
    Map<String, dynamic>? body,
    T Function(dynamic)? fromJson,
    bool auth = true,
  }) async {
    final res = await http.post(
      Uri.parse('$baseUrl$path'),
      headers: await _headers(auth: auth),
      body: body != null ? json.encode(body) : null,
    );
    return _handleResponse(res, fromJson ?? (j) => j as T);
  }

  static Future<T> patch<T>(
    String path, {
    Map<String, dynamic>? body,
    T Function(dynamic)? fromJson,
    bool auth = true,
  }) async {
    final res = await http.patch(
      Uri.parse('$baseUrl$path'),
      headers: await _headers(auth: auth),
      body: body != null ? json.encode(body) : null,
    );
    return _handleResponse(res, fromJson ?? (j) => j as T);
  }

  static Future<T> delete<T>(
    String path, {
    T Function(dynamic)? fromJson,
    bool auth = true,
  }) async {
    final res = await http.delete(
      Uri.parse('$baseUrl$path'),
      headers: await _headers(auth: auth),
    );
    return _handleResponse(res, fromJson ?? (j) => j as T);
  }

  /// POST multipart para archivos (fotos + audio de incidentes CU7).
  static Future<T> postMultipart<T>(
    String path, {
    required Map<String, String> fields,
    List<MapEntry<String, File>>? files,
    T Function(dynamic)? fromJson,
  }) async {
    final token = await getToken();
    final request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl$path'),
    );
    if (token != null) {
      request.headers['Authorization'] = 'Bearer $token';
    }
    request.fields.addAll(fields);
    if (files != null) {
      for (final entry in files) {
        request.files.add(
          await http.MultipartFile.fromPath(entry.key, entry.value.path),
        );
      }
    }
    final streamed = await request.send();
    final res = await http.Response.fromStream(streamed);
    return _handleResponse(res, fromJson ?? (j) => j as T);
  }
}
