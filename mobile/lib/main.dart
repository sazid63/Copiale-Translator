/// Copiale Translator — offline cipher messenger with optional locked mode.
library;

import 'package:flutter/material.dart';

import 'ui/about_screen.dart';
import 'ui/cipher_screen.dart';
import 'ui/symbols_screen.dart';
import 'ui/theme.dart';

void main() {
  runApp(const CopialeApp());
}

class CopialeApp extends StatelessWidget {
  const CopialeApp({super.key});

  @override
  Widget build(BuildContext context) {
    final scheme = ColorScheme.dark(
      primary: NightSignals.primary,
      secondary: NightSignals.amber,
      surface: NightSignals.surface,
      error: NightSignals.danger,
    );
    return MaterialApp(
      title: 'Copiale Translator',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        colorScheme: scheme,
        scaffoldBackgroundColor: NightSignals.bg,
        appBarTheme: const AppBarTheme(
          backgroundColor: NightSignals.bg,
          foregroundColor: NightSignals.text,
          elevation: 0,
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: NightSignals.surface,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: const BorderSide(color: NightSignals.line),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: const BorderSide(color: NightSignals.line),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide:
                const BorderSide(color: NightSignals.primary, width: 1.5),
          ),
          hintStyle: const TextStyle(color: NightSignals.muted),
        ),
        filledButtonTheme: FilledButtonThemeData(
          style: FilledButton.styleFrom(
            backgroundColor: NightSignals.primary,
            foregroundColor: const Color(0xFF06231C),
            padding: const EdgeInsets.symmetric(vertical: 16),
            shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12)),
            textStyle:
                const TextStyle(fontWeight: FontWeight.w700, fontSize: 16),
          ),
        ),
        outlinedButtonTheme: OutlinedButtonThemeData(
          style: OutlinedButton.styleFrom(
            foregroundColor: NightSignals.text,
            side: const BorderSide(color: NightSignals.line),
            shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12)),
          ),
        ),
        switchTheme: SwitchThemeData(
          thumbColor: WidgetStateProperty.resolveWith((s) =>
              s.contains(WidgetState.selected)
                  ? NightSignals.primary
                  : NightSignals.muted),
          trackColor: WidgetStateProperty.resolveWith((s) =>
              s.contains(WidgetState.selected)
                  ? NightSignals.primaryDim
                  : NightSignals.surface2),
        ),
        snackBarTheme: const SnackBarThemeData(
          backgroundColor: NightSignals.surface2,
          contentTextStyle: TextStyle(color: NightSignals.text),
        ),
      ),
      home: const HomeShell(),
    );
  }
}

class HomeShell extends StatefulWidget {
  const HomeShell({super.key});
  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> {
  int _index = 0;

  static const _titles = ['Cipher', 'Symbols', 'About'];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Container(
              width: 10,
              height: 10,
              decoration: const BoxDecoration(
                color: NightSignals.primary,
                shape: BoxShape.circle,
              ),
            ),
            const SizedBox(width: 10),
            Text(
              _titles[_index].toUpperCase(),
              style: const TextStyle(
                  letterSpacing: 3,
                  fontSize: 15,
                  fontWeight: FontWeight.w600),
            ),
          ],
        ),
        actions: const [
          Padding(
            padding: EdgeInsets.only(right: 16),
            child: Center(
              child: Text('OFFLINE',
                  style: TextStyle(
                      color: NightSignals.muted,
                      fontSize: 11,
                      letterSpacing: 2)),
            ),
          ),
        ],
      ),
      body: IndexedStack(
        index: _index,
        children: const [
          CipherScreen(),
          SymbolsScreen(),
          AboutScreen(),
        ],
      ),
      bottomNavigationBar: NavigationBar(
        backgroundColor: NightSignals.bg,
        indicatorColor: NightSignals.surface2,
        selectedIndex: _index,
        onDestinationSelected: (i) => setState(() => _index = i),
        destinations: const [
          NavigationDestination(
              icon: Icon(Icons.swap_horiz), label: 'Cipher'),
          NavigationDestination(
              icon: Icon(Icons.grid_view), label: 'Symbols'),
          NavigationDestination(
              icon: Icon(Icons.info_outline), label: 'About'),
        ],
      ),
    );
  }
}
