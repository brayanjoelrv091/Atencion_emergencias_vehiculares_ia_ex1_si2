/// CU18 — Pasarela de Pago en línea (simulada).
///
/// POST /payments/process
/// Requiere: incidente_id, monto, moneda, metodo_pago
library;

import 'package:flutter/material.dart';

import '../../../core/api_client.dart';

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
  String? _transaccionId;
  String? _errorMsg;

  String _metodoPago = 'tarjeta';
  String _moneda = 'USD';

  static const _metodos = ['tarjeta', 'transferencia', 'efectivo'];
  static const _monedas = ['USD', 'CLP', 'EUR'];

  Future<void> _processPayment() async {
    setState(() {
      _isProcessing = true;
      _errorMsg = null;
    });

    try {
      final result = await ApiClient.post<Map<String, dynamic>>(
        '/payments/process',
        body: {
          'incidente_id': widget.incidentId,
          'monto': widget.amount,
          'moneda': _moneda,
          'metodo_pago': _metodoPago,
        },
        fromJson: (j) => j as Map<String, dynamic>,
      );
      setState(() {
        _isSuccess = true;
        _transaccionId = result['transaccion_id'] as String?;
      });
    } on ApiException catch (e) {
      setState(() => _errorMsg = e.message);
    } finally {
      if (mounted) setState(() => _isProcessing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0E1A),
      appBar: AppBar(
        title: const Text('Pasarela de Pago'),
        backgroundColor: const Color(0xFF111629),
        foregroundColor: const Color(0xFF00F2FF),
      ),
      body: Center(
        child: _isSuccess ? _buildSuccess() : _buildForm(),
      ),
    );
  }

  Widget _buildForm() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const SizedBox(height: 20),
          // Ícono y monto
          Center(
            child: Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: const Color(0xFF00F2FF).withValues(alpha: 0.08),
                shape: BoxShape.circle,
                border: Border.all(
                  color: const Color(0xFF00F2FF).withValues(alpha: 0.3),
                  width: 2,
                ),
              ),
              child: const Icon(
                Icons.account_balance_wallet,
                size: 52,
                color: Color(0xFF00F2FF),
              ),
            ),
          ),
          const SizedBox(height: 20),
          Center(
            child: Text(
              '\$${widget.amount.toStringAsFixed(2)}',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 36,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          Center(
            child: Text(
              'Incidente #${widget.incidentId}',
              style: const TextStyle(color: Colors.white38, fontSize: 14),
            ),
          ),
          const SizedBox(height: 30),

          // Selector de moneda
          _buildSectionLabel('Moneda'),
          const SizedBox(height: 8),
          Row(
            children: _monedas.map((m) => Padding(
              padding: const EdgeInsets.only(right: 8),
              child: ChoiceChip(
                label: Text(m),
                selected: _moneda == m,
                onSelected: (_) => setState(() => _moneda = m),
                selectedColor: const Color(0xFF00F2FF),
                backgroundColor: const Color(0xFF111629),
                labelStyle: TextStyle(
                  color: _moneda == m ? Colors.black : Colors.white70,
                  fontWeight: FontWeight.w600,
                ),
              ),
            )).toList(),
          ),
          const SizedBox(height: 20),

          // Selector de método de pago
          _buildSectionLabel('Método de Pago'),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            children: _metodos.map((m) => ChoiceChip(
              label: Text(m),
              selected: _metodoPago == m,
              onSelected: (_) => setState(() => _metodoPago = m),
              selectedColor: const Color(0xFF00F2FF),
              backgroundColor: const Color(0xFF111629),
              labelStyle: TextStyle(
                color: _metodoPago == m ? Colors.black : Colors.white70,
              ),
            )).toList(),
          ),

          if (_errorMsg != null) ...[
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFFFF6B6B).withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: const Color(0xFFFF6B6B).withValues(alpha: 0.4)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.error_outline, color: Color(0xFFFF6B6B), size: 18),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      _errorMsg!,
                      style: const TextStyle(color: Color(0xFFFF6B6B), fontSize: 13),
                    ),
                  ),
                ],
              ),
            ),
          ],

          const SizedBox(height: 30),
          SizedBox(
            height: 54,
            child: ElevatedButton(
              onPressed: _isProcessing ? null : _processPayment,
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF00F2FF),
                foregroundColor: Colors.black,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14),
                ),
              ),
              child: _isProcessing
                  ? const CircularProgressIndicator(color: Colors.black, strokeWidth: 2)
                  : const Text(
                      'PAGAR AHORA',
                      style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                    ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSuccess() {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.all(24),
            decoration: const BoxDecoration(
              color: Color(0xFF00C853),
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.check, size: 60, color: Colors.white),
          ),
          const SizedBox(height: 24),
          const Text(
            'PAGO EXITOSO',
            style: TextStyle(
              color: Colors.white,
              fontSize: 26,
              fontWeight: FontWeight.bold,
              letterSpacing: 1,
            ),
          ),
          const SizedBox(height: 10),
          Text(
            'Tu servicio ha sido liquidado.',
            style: TextStyle(color: Colors.white.withValues(alpha: 0.6)),
          ),
          if (_transaccionId != null) ...[
            const SizedBox(height: 20),
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: const Color(0xFF111629),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.receipt_long, color: Color(0xFF00F2FF), size: 18),
                  const SizedBox(width: 8),
                  Text(
                    'TX: $_transaccionId',
                    style: const TextStyle(
                      color: Color(0xFF00F2FF),
                      fontFamily: 'monospace',
                      fontSize: 13,
                    ),
                  ),
                ],
              ),
            ),
          ],
          const SizedBox(height: 40),
          OutlinedButton.icon(
            onPressed: () => Navigator.pop(context),
            icon: const Icon(Icons.arrow_back),
            label: const Text('VOLVER'),
            style: OutlinedButton.styleFrom(
              foregroundColor: const Color(0xFF00F2FF),
              side: const BorderSide(color: Color(0xFF00F2FF)),
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionLabel(String text) {
    return Text(
      text,
      style: const TextStyle(
        color: Colors.white54,
        fontSize: 12,
        fontWeight: FontWeight.w600,
        letterSpacing: 0.5,
      ),
    );
  }
}
