import 'package:flutter/material.dart';

import 'screens/app_shell.dart';
import 'theme/app_theme.dart';

void main() {
  runApp(const FilmPhotographyApp());
}

class FilmPhotographyApp extends StatelessWidget {
  const FilmPhotographyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Filmly',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      home: const AppShell(),
    );
  }
}

