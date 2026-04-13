import 'package:flutter_test/flutter_test.dart';

import 'package:rutaigeoproxi_mobile/main.dart';

void main() {
  testWidgets('Muestra pantalla de login', (WidgetTester tester) async {
    await tester.pumpWidget(const RutaiApp(initialLoggedIn: false));
    expect(find.textContaining('Login'), findsOneWidget);
  });
}
