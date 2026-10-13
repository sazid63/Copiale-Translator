/// About: what the cipher is, what is historical vs modern, and how the
/// locked exchange works. Honesty first — same rules as the desktop project.
library;

import 'package:flutter/material.dart';

import 'theme.dart';

class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: const [
        _Block(
          title: 'THE CIPHER',
          body:
              'The Copiale cipher is a real historical code from the 1700s, decoded by researchers in 2011 (Knight, Megyesi & Schaefer). '
              'It swaps each letter for strange symbols. This app speaks those symbols using plain-text tokens.',
        ),
        _Block(
          title: 'HOW TO SEND A SECRET',
          body:
              '1. Type your message and add a key (or tap Generate key).\n'
              '2. Tap Encode, then Send — the app shares the cipher text AND the key.\n'
              '3. Your contact pastes both into their Decode screen with the same key.\n'
              'Without the key, the same cipher text reads as gibberish.',
        ),
        _Block(
          title: 'WHAT IS HISTORICAL, WHAT IS NOT',
          body:
              'Historical: the letter symbols, the : doubling rule, the period mark, the logograms (star, lip, …).\n'
              'Modern extensions, always labelled: English text, German number words, the punctuation , ? ! ; = — and the shared-key lock. '
              'Locked messages are still ordinary cipher symbols; the key only scrambles the letters underneath.',
        ),
        _Block(
          title: 'HONEST LIMITS',
          body:
              'The shared key is a casual-privacy convenience, not audited cryptography — do not use it for anything that needs real security. '
              'Numbers arrive as German words (2 → zwei). Capital letters are not preserved. '
              'This app works fully offline and sends nothing anywhere by itself.',
        ),
        SizedBox(height: 24),
      ],
    );
  }
}

class _Block extends StatelessWidget {
  final String title;
  final String body;
  const _Block({required this.title, required this.body});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: NightSignals.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: NightSignals.line),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title,
              style: const TextStyle(
                  color: NightSignals.primary,
                  fontSize: 12,
                  letterSpacing: 2,
                  fontWeight: FontWeight.w700)),
          const SizedBox(height: 8),
          Text(body,
              style:
                  const TextStyle(color: NightSignals.text, height: 1.55)),
        ],
      ),
    );
  }
}
