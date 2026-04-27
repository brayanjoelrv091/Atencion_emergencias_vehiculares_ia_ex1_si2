import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:rutaigeoproxi_mobile/config.dart';

class PaymentScreen extends StatefulWidget {
  final int incidentId;
  final double amount;

  const PaymentScreen({
    super.key,
    required this.incidentId,
    required this.amount,
  });

  @override
  State<PaymentScreen> createState() => _PaymentScreenState();
}

class _PaymentScreenState extends State<PaymentScreen> {
  bool _isProcessing = false;
  bool _isSuccess = false;

  Future<void> _processPayment() async {
    setState(() => _isProcessing = true);

    try {
      final response = await http.post(
        Uri.parse('${AppConfig.baseUrl}/payments/process'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'incidente_id': widget.incidentId,
          'monto': widget.amount,
          'metodo_pago': 'tarjeta_mobile',
        }),
      );

      if (response.statusCode == 201) {
        setState(() {
          _isProcessing = false;
          _isSuccess = true;
        });
      } else {
        throw Exception('Error en el servidor');
      }
    } catch (e) {
      setState(() => _isProcessing = false);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error al procesar pago: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0E1A),
      appBar: AppBar(
        title: const Text('Pasarela de Pago'),
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: Center(
        child: _isSuccess ? _buildSuccess() : _buildForm(),
      ),
    );
  }

  Widget _buildForm() {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(
            Icons.account_balance_wallet,
            size: 80,
            color: Color(0xFF00F2FF),
          ),
          const SizedBox(height: 20),
          Text(
            'Monto a Pagar: \$${widget.amount.toStringAsFixed(2)}',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 22,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 40),
          _buildField('Titular', 'NOMBRE EN TARJETA'),
          const SizedBox(height: 15),
          _buildField('Numero', '0000 0000 0000 0000'),
          const SizedBox(height: 30),
          ElevatedButton(
            onPressed: _isProcessing ? null : _processPayment,
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF00F2FF),
              foregroundColor: Colors.black,
              minimumSize: const Size(double.infinity, 55),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            child: _isProcessing
                ? const CircularProgressIndicator(color: Colors.black)
                : const Text(
                    'PAGAR AHORA',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildField(String label, String hint) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(color: Colors.white70, fontSize: 12),
        ),
        const SizedBox(height: 5),
        TextField(
          decoration: InputDecoration(
            hintText: hint,
            hintStyle: const TextStyle(color: Colors.white24),
            filled: true,
            fillColor: Colors.white.withValues(alpha: 0.05),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide.none,
            ),
          ),
          style: const TextStyle(color: Colors.white),
          readOnly: true,
        ),
      ],
    );
  }

  Widget _buildSuccess() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        const Icon(
          Icons.check_circle_outline,
          size: 100,
          color: Colors.greenAccent,
        ),
        const SizedBox(height: 20),
        const Text(
          'PAGO EXITOSO',
          style: TextStyle(
            color: Colors.white,
            fontSize: 24,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 10),
        const Text(
          'Tu servicio ha sido liquidado correctamente.',
          style: TextStyle(color: Colors.white70),
        ),
        const SizedBox(height: 40),
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text(
            'VOLVER AL INICIO',
            style: TextStyle(color: Color(0xFF00F2FF)),
          ),
        ),
      ],
    );
  }
}
