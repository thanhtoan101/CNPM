import 'package:film_photography_mobile/main.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('shows the photographer navigation and home content', (tester) async {
    await tester.pumpWidget(const FilmPhotographyApp());

    expect(find.text('Filmly'), findsOneWidget);
    expect(find.text('Recommended Film Labs'), findsOneWidget);
    expect(find.text('Home'), findsOneWidget);
    expect(find.text('Orders'), findsOneWidget);
    expect(find.text('Archive'), findsOneWidget);
    expect(find.text('Market'), findsOneWidget);
    expect(find.text('Profile'), findsOneWidget);
  });
}
