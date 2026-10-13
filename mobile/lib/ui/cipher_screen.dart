/// The encode / decode workspace: message in, tokens out (and back),
/// with the optional shared key that makes the exchange private.
library;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:share_plus/share_plus.dart';

import '../copiale/cipher.dart';
import '../copiale/errors.dart';
import '../copiale/locked.dart';
import 'theme.dart';

enum Direction { encode, decode }

class CipherScreen extends StatefulWidget {
  const CipherScreen({super.key});
  @override
  State<CipherScreen> createState() => _CipherScreenState();
}

class _CipherScreenState extends State<CipherScreen> {
  Direction _dir = Direction.encode;
  final _input = TextEditingController();
  final _key = TextEditingController();
  bool _strict = false;
  bool _obscureKey = true;
  String? _output;
  String? _meta;
  String? _error;

  @override
  void dispose() {
    _input.dispose();
    _key.dispose();
    super.dispose();
  }

  String? get _effectiveKey {
    final k = _key.text.trim();
    return k.isEmpty ? null : k;
  }

  void _run() {
    final text = _input.text.trim();
    if (text.isEmpty) {
      setState(() {
        _error = 'Type or paste something first.';
        _output = null;
        _meta = null;
      });
      return;
    }
    final mode = _strict ? 'strict' : 'experimental';
    try {
      if (_dir == Direction.encode) {
        final res = encode(text, mode: mode, key: _effectiveKey);
        setState(() {
          _output = render(res.tokens);
          _error = null;
          _meta = _effectiveKey != null
              ? '${res.tokens.length} tokens · locked — send the tokens AND the key'
              : '${res.tokens.length} tokens'
                  '${res.extensions.isNotEmpty ? ' · ${res.extensions.join(', ')}' : ''}';
        });
      } else {
        final res = decode(text, mode: mode, key: _effectiveKey);
        setState(() {
          _output = res.text;
          _error = null;
          _meta = _effectiveKey != null
              ? 'unlocked with key'
              : (res.unknown.isNotEmpty
                  ? 'unknown tokens: ${res.unknown.join(', ')}'
                  : 'decoded');
        });
      }
    } on CopialeError catch (e) {
      setState(() {
        _error = e.message;
        _output = null;
        _meta = null;
      });
    }
  }

  Future<void> _paste(TextEditingController c) async {
    final data = await Clipboard.getData(Clipboard.kTextPlain);
    if (data?.text != null) {
      c.text = data!.text!;
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Pasted from clipboard')));
      }
    }
  }

  Future<void> _copy(String text, String label) async {
    await Clipboard.setData(ClipboardData(text: text));
    if (mounted) {
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text('$label copied')));
    }
  }

  void _share() {
    final out = _output;
    if (out == null) return;
    final k = _effectiveKey;
    final msg = k != null
        ? 'Copiale cipher message:\n$out\n\nKey: $k\n\nOpen in Copiale Translator and decode with this key.'
        : 'Copiale cipher message:\n$out';
    Share.share(msg, subject: 'Copiale cipher message');
  }

  @override
  Widget build(BuildContext context) {
    final isEncode = _dir == Direction.encode;
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        SegmentedButton<Direction>(
          segments: const [
            ButtonSegment(
                value: Direction.encode,
                label: Text('ENCODE'),
                icon: Icon(Icons.lock_outline)),
            ButtonSegment(
                value: Direction.decode,
                label: Text('DECODE'),
                icon: Icon(Icons.lock_open_outlined)),
          ],
          selected: {_dir},
          onSelectionChanged: (s) => setState(() {
            _dir = s.first;
            _output = null;
            _meta = null;
            _error = null;
          }),
          style: SegmentedButton.styleFrom(
            selectedBackgroundColor: NightSignals.surface2,
            selectedForegroundColor: NightSignals.primary,
            foregroundColor: NightSignals.muted,
          ),
        ),
        const SizedBox(height: 14),
        Row(
          children: [
            Expanded(
              child: Text(
                isEncode
                    ? 'Your message (plain English or German)'
                    : 'Cipher tokens (paste what you received)',
                style: const TextStyle(
                    color: NightSignals.muted, fontSize: 12, letterSpacing: 1),
              ),
            ),
            TextButton.icon(
              onPressed: () => _paste(_input),
              icon: const Icon(Icons.content_paste, size: 16),
              label: const Text('Paste'),
            ),
          ],
        ),
        const SizedBox(height: 6),
        TextField(
          controller: _input,
          minLines: 4,
          maxLines: 8,
          style: const TextStyle(fontSize: 16, height: 1.5),
          decoration: InputDecoration(
            hintText: isEncode
                ? 'meet at midnight'
                : 'sqi car : qua a pi qua b …',
          ),
        ),
        const SizedBox(height: 14),
        const Text('Shared key (optional)',
            style: TextStyle(
                color: NightSignals.muted, fontSize: 12, letterSpacing: 1)),
        const SizedBox(height: 6),
        TextField(
          controller: _key,
          obscureText: _obscureKey,
          decoration: InputDecoration(
            hintText: 'leave empty for an open message',
            prefixIcon: const Icon(Icons.key_outlined,
                color: NightSignals.amber, size: 20),
            suffixIcon: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                IconButton(
                  tooltip: 'Show / hide key',
                  onPressed: () =>
                      setState(() => _obscureKey = !_obscureKey),
                  icon: Icon(
                      _obscureKey
                          ? Icons.visibility_outlined
                          : Icons.visibility_off_outlined,
                      size: 20),
                ),
                IconButton(
                  tooltip: 'Copy key',
                  onPressed: _key.text.isEmpty
                      ? null
                      : () => _copy(_key.text, 'Key'),
                  icon: const Icon(Icons.copy_outlined, size: 20),
                ),
              ],
            ),
          ),
          onChanged: (_) => setState(() {}),
        ),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: OutlinedButton.icon(
                onPressed: () {
                  _key.text = generateKey();
                  setState(() {});
                },
                icon: const Icon(Icons.autorenew, size: 18),
                label: const Text('Generate key'),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Row(
                children: [
                  const Text('Strict',
                      style: TextStyle(color: NightSignals.muted)),
                  const SizedBox(width: 6),
                  Switch(
                    value: _strict,
                    onChanged: (v) => setState(() => _strict = v),
                  ),
                ],
              ),
            ),
          ],
        ),
        const SizedBox(height: 14),
        SizedBox(
          width: double.infinity,
          child: FilledButton.icon(
            onPressed: _run,
            icon: Icon(isEncode ? Icons.enhanced_encryption : Icons.lock_open_outlined),
            label: Text(isEncode ? 'Encode message' : 'Decode message'),
          ),
        ),
        if (_error != null) ...[
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: NightSignals.surface,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: NightSignals.danger.withValues(alpha: 0.6)),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.error_outline,
                    color: NightSignals.danger, size: 20),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(_error!,
                      style: const TextStyle(
                          color: NightSignals.text, height: 1.4)),
                ),
              ],
            ),
          ),
        ],
        if (_output != null) ...[
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: NightSignals.surface,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                  color: _effectiveKey != null
                      ? NightSignals.amber.withValues(alpha: 0.6)
                      : NightSignals.primaryDim),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (_meta != null)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: Text(_meta!,
                        style: TextStyle(
                            color: _effectiveKey != null
                                ? NightSignals.amber
                                : NightSignals.primary,
                            fontSize: 12,
                            letterSpacing: 0.5)),
                  ),
                SelectableText(_output!,
                    style: const TextStyle(fontSize: 16, height: 1.6)),
                const SizedBox(height: 10),
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () => _copy(
                            _output!, isEncode ? 'Tokens' : 'Message'),
                        icon: const Icon(Icons.copy_outlined, size: 18),
                        label: const Text('Copy'),
                      ),
                    ),
                    if (isEncode) ...[
                      const SizedBox(width: 10),
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: _share,
                          icon: const Icon(Icons.share_outlined, size: 18),
                          label: const Text('Send'),
                        ),
                      ),
                    ],
                  ],
                ),
              ],
            ),
          ),
        ],
        const SizedBox(height: 24),
      ],
    );
  }
}
