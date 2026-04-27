import 'package:flutter_test/flutter_test.dart';

import 'package:rutaigeoproxi_mobile/main.dart';

void main() {
  testWidgets('Muestra el splash inicial', (WidgetTester tester) async {
    await tester.pumpWidget(const RutAIGeoProxiApp());
    await tester.pump(const Duration(milliseconds: 350));
    expect(find.text('RutAIGeoProxi'), findsOneWidget);
  });
}
