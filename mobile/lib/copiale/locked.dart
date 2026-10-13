/// Optional user-key layer (modern extension E6).
///
/// Byte-for-byte compatible with copiale/locked.py ("Copiale-Lock-v2"):
/// the permutation of the 29-letter alphabet comes from a Fisher-Yates
/// shuffle driven by a SHA-256 counter stream. Block c =
/// SHA256("Copiale-Lock-v2" + 0x00 + key_utf8 + counter_be32), consumed as
/// consecutive big-endian uint32 words; each position i (n-1 down to 1)
/// takes j = randbelow(i+1) via rejection sampling on the top
/// bit_length(limit-1) bits of the next word.
library;

import 'dart:convert';
import 'dart:math';
import 'dart:typed_data';

import 'package:crypto/crypto.dart';

import 'errors.dart';

/// Letters covered by the substitution (ß normalises to "ss" first,
/// exactly as in unlocked mode).
const String lockedAlphabet = 'abcdefghijklmnopqrstuvwxyzäöü';

/// Derivation version tag (domain separation).
const String lockedDerivation = 'Copiale-Lock-v2';

const String _keygenAlphabet =
    'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
const int defaultKeyLength = 16;
const int minKeyLength = 4;
const int maxKeyLength = 128;

void validateKey(String? key) {
  if (key == null || key.trim().isEmpty) {
    throw CopialeError('key must be a non-empty string');
  }
}

/// Infinite stream of uint32 words (big-endian) from the SHA-256 counter
/// stream. Yields lazily so callers only hash as many blocks as needed.
Iterable<int> _words(String key) sync* {
  final kb = utf8.encode(key);
  var counter = 0;
  while (true) {
    final input = BytesBuilder()
      ..add(utf8.encode(lockedDerivation))
      ..addByte(0)
      ..add(kb)
      ..add(_be32(counter));
    final digest = sha256.convert(input.toBytes()).bytes;
    for (var i = 0; i < 32; i += 4) {
      yield (digest[i] << 24) |
          (digest[i + 1] << 16) |
          (digest[i + 2] << 8) |
          digest[i + 3];
    }
    counter++;
  }
}

Uint8List _be32(int v) {
  final b = ByteData(4)..setUint32(0, v);
  return b.buffer.asUint8List();
}

/// Deterministic permutation of [lockedAlphabet] derived from [key].
String lockedPermutation(String key) {
  validateKey(key);
  final perm = lockedAlphabet.runes.toList();
  final stream = _words(key).iterator;
  for (var i = perm.length - 1; i >= 1; i--) {
    final limit = i + 1;
    final k = (limit - 1).bitLength;
    int j;
    while (true) {
      stream.moveNext();
      final cand = stream.current >> (32 - k);
      if (cand < limit) {
        j = cand;
        break;
      }
    }
    final t = perm[i];
    perm[i] = perm[j];
    perm[j] = t;
  }
  return String.fromCharCodes(perm);
}

/// Substitute every alphabet letter of [text] using [key].
String lockedApply(String text, String key) {
  final perm = lockedPermutation(key);
  final from = lockedAlphabet.runes.toList();
  final to = perm.runes.toList();
  final table = <int, int>{for (var i = 0; i < from.length; i++) from[i]: to[i]};
  return String.fromCharCodes(text.runes.map((c) => table[c] ?? c));
}

final RegExp _protected = RegExp(r'(\*[^*]*\*|‹[^›]*›)');

/// Inverse of [lockedApply], leaving `*...*` and `‹?..?›` spans intact.
String lockedUnapply(String text, String key) {
  final perm = lockedPermutation(key);
  final from = perm.runes.toList();
  final to = lockedAlphabet.runes.toList();
  final table = <int, int>{for (var i = 0; i < from.length; i++) from[i]: to[i]};
  final parts = <String>[];
  var last = 0;
  for (final m in _protected.allMatches(text)) {
    parts.add(String.fromCharCodes(
        text.substring(last, m.start).runes.map((c) => table[c] ?? c)));
    parts.add(m.group(0)!);
    last = m.end;
  }
  parts.add(String.fromCharCodes(
      text.substring(last).runes.map((c) => table[c] ?? c)));
  return parts.join();
}

/// Generate a random shareable key (ASCII letters + digits).
String generateKey([int length = defaultKeyLength]) {
  if (length < minKeyLength || length > maxKeyLength) {
    throw CopialeError(
        'key length must be an integer between $minKeyLength and $maxKeyLength');
  }
  final rng = Random.secure();
  final chars = _keygenAlphabet.codeUnits;
  return String.fromCharCodes(
      List.generate(length, (_) => chars[rng.nextInt(chars.length)]));
}
