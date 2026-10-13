/// Browse the symbol inventory: letters, units, logograms, spaces.
library;

import 'package:flutter/material.dart';

import '../copiale/key_data.dart' as kdata;
import 'theme.dart';

class SymbolsScreen extends StatelessWidget {
  const SymbolsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const _Hint(
            'Every token the app reads or writes. Historical items are from the 2011 key; the five punctuation marks are modern extensions.'),
        const SizedBox(height: 12),
        _Section(
          title: 'LETTERS',
          child: Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              for (final e in kdata.histLetterHomophones.entries)
                _Chip('${e.key}  →  ${e.value.join('  ')}'),
            ],
          ),
        ),
        _Section(
          title: 'MULTI-LETTER UNITS',
          child: Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              for (var i = 0; i < kdata.histMultiUnits.length; i++)
                _Chip(
                    '${kdata.histMultiUnits[i]}  →  ${kdata.histMultiTokens[i]}'),
            ],
          ),
        ),
        const _Section(
          title: 'REPEAT',
          child: Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [_Chip(':  doubles the previous consonant')],
          ),
        ),
        _Section(
          title: 'LOGOGRAMS',
          child: Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              for (final e in kdata.logoTokens.entries)
                _Chip('${e.key}  →  ${e.value}'),
            ],
          ),
        ),
        _Section(
          title: 'MODERN PUNCTUATION (EXTENSION)',
          child: Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              for (final e in kdata.extendedPunct.entries)
                _Chip('${e.key}  →  ${e.value}'),
            ],
          ),
        ),
        const SizedBox(height: 24),
      ],
    );
  }
}

class _Section extends StatelessWidget {
  final String title;
  final Widget child;
  const _Section({required this.title, required this.child});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title,
              style: const TextStyle(
                  color: NightSignals.muted,
                  fontSize: 12,
                  letterSpacing: 2,
                  fontWeight: FontWeight.w600)),
          const SizedBox(height: 8),
          child,
        ],
      ),
    );
  }
}

class _Chip extends StatelessWidget {
  final String text;
  const _Chip(this.text);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: NightSignals.surface,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: NightSignals.line),
      ),
      child: Text(text, style: const TextStyle(fontSize: 14)),
    );
  }
}

class _Hint extends StatelessWidget {
  final String text;
  const _Hint(this.text);

  @override
  Widget build(BuildContext context) {
    return Text(text,
        style: const TextStyle(color: NightSignals.muted, height: 1.5));
  }
}
