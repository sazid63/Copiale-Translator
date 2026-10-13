/// Copiale translator: encode and decode (port of copiale/translate.py).
///
/// Two modes:
///   strict       - only historically documented features. Numerals and the
///                  modern punctuation extensions are REJECTED.
///   experimental - additionally enables the approved extensions.
///
/// Nothing is ever dropped silently: unsupported input throws CopialeError.
///
/// Port-fidelity notes (deliberate quirks preserved from Python):
/// - `\d` matches ASCII digits only (Python matches Unicode digits).
/// - Huge integers (>= 2^63) are rejected with the same "number too large"
///   message Python raises via spell_int.
/// - `numberLang` exists in Python but is unused; it is not ported.
library;

import 'errors.dart';
import 'key_data.dart' as kdata;
import 'locked.dart';
import 'numbers.dart';

/// Consonants for the ":" repeat rule (mirrors Python CONSONANTS).
const Set<String> consonants = {
  'b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q',
  'r', 's', 't', 'v', 'w', 'x', 'y', 'z', 'ß',
};

const String _letters = 'abcdefghijklmnopqrstuvwxyzäöüß';

final RegExp _numRe = RegExp(r'[+-]?\d+(?:[.,]\d+)?');
final RegExp _digitRe = RegExp(r'\d');
final RegExp _spaceRuns = RegExp(r'  +');

String render(List<String> tokens) => tokens.join(' ');

class EncodeResult {
  final List<String> tokens;
  final String text;
  final List<String> extensions;
  final List<String> unsupported;
  final List<String> notes;
  final bool locked;
  EncodeResult({
    required this.tokens,
    required this.text,
    required this.extensions,
    required this.unsupported,
    required this.notes,
    required this.locked,
  });
}

class DecodeResult {
  final String text;
  final List<String> notes;
  final List<String> extensions;
  final List<(String, String)> ambiguous;
  final List<String> unknown;
  final bool locked;
  DecodeResult({
    required this.text,
    required this.notes,
    required this.extensions,
    required this.ambiguous,
    required this.unknown,
    required this.locked,
  });
}

String _chooseHomophone(String letter, Map<String, int> counters) {
  final toks = kdata.histLetterHomophones[letter]!;
  final i = counters[letter] ?? 0;
  counters[letter] = i + 1;
  return toks[i % toks.length];
}

/// Encode one lowercase word; returns tokens with null for unsupported chars.
List<String?> _encodeWord(String word, Map<String, int> counters,
    bool useColon, List<String> unsupported) {
  final tokens = <String?>[];
  final letters = <String>[];
  final runes = word.runes.toList();
  var i = 0;
  while (i < runes.length) {
    var matched = false;
    for (var u = 0; u < kdata.histMultiUnits.length; u++) {
      final unit = kdata.histMultiUnits[u];
      final ur = unit.runes.toList();
      if (i + ur.length <= runes.length) {
        var same = true;
        for (var j = 0; j < ur.length; j++) {
          if (runes[i + j] != ur[j]) {
            same = false;
            break;
          }
        }
        if (same) {
          tokens.add(kdata.histMultiTokens[u]);
          letters.add(unit);
          i += ur.length;
          matched = true;
          break;
        }
      }
    }
    if (matched) continue;
    final ch = String.fromCharCode(runes[i]);
    if (kdata.histLetterHomophones.containsKey(ch)) {
      tokens.add(_chooseHomophone(ch, counters));
      letters.add(ch);
    } else {
      unsupported.add(ch);
      tokens.add(null);
      letters.add(ch);
    }
    i += 1;
  }

  if (useColon) {
    var j = 1;
    while (j < tokens.length) {
      if (letters[j] == letters[j - 1] &&
          consonants.contains(letters[j]) &&
          tokens[j] != null &&
          letters[j - 1].runes.length == 1) {
        tokens[j] = kdata.repeatToken;
      }
      j += 1;
    }
  }
  return tokens;
}

String _spellNumberToken(String tok, List<String> extensions) {
  extensions.add('numerals->german');
  final bare = tok.startsWith('+') || tok.startsWith('-')
      ? tok.substring(1)
      : tok;
  if (bare.startsWith('.')) return tok;
  if (tok.contains('.') || tok.contains(',')) return spellDecimal(tok);
  // Mirror Python: arbitrary-precision parse, then range-check in spellInt.
  var digits = bare;
  digits = digits.replaceFirst(RegExp(r'^0+'), '');
  if (digits.length > 18) {
    throw StateError('number too large for German spelling (>=10^15)');
  }
  return spellInt(int.parse(tok));
}

EncodeResult encode(String text,
    {String mode = 'experimental',
    bool spellNumbers = true,
    bool useColon = true,
    String? key}) {
  if (mode != 'strict' && mode != 'experimental') {
    throw ArgumentError("mode must be 'strict' or 'experimental'");
  }
  if (key != null) validateKey(key);
  if (key != null && mode == 'strict') {
    throw CopialeError('keys are a modern extension, rejected in strict mode');
  }

  final notes = <String>[];
  final extensions = <String>[];
  final unsupported = <String>[];

  var s = text.toLowerCase().replaceAll('\u2019', "'");

  if (spellNumbers && mode == 'experimental') {
    s = s.replaceAllMapped(
        _numRe, (m) => _spellNumberToken(m.group(0)!, extensions));
  } else if (_digitRe.hasMatch(s)) {
    if (mode == 'strict') {
      final digs = _digitRe
          .allMatches(s)
          .map((m) => m.group(0)!)
          .toSet()
          .toList()
        ..sort();
      unsupported.addAll(digs);
      notes.add('digits are not part of the historical cipher');
    }
  }

  if (key != null) {
    // After number spelling so spelled-out number words are covered too.
    // ß normalises to "ss" first (same documented rule as unlocked mode).
    s = lockedApply(s.replaceAll('ß', 'ss'), key);
    extensions.add('locked-key');
  }

  final counters = <String, int>{};
  final tokens = <String>[];
  final word = <int>[];
  var spaceI = 0;

  String nextSpace() {
    final t = kdata.spaceChoices[spaceI % kdata.spaceChoices.length];
    spaceI += 1;
    return t;
  }

  void flush() {
    if (word.isNotEmpty) {
      final toks = _encodeWord(
          String.fromCharCodes(word), counters, useColon, unsupported);
      for (final t in toks) {
        tokens.add(t ?? '<?>');
      }
      word.clear();
    }
  }

  for (final r in s.runes) {
    final ch = String.fromCharCode(r);
    if (ch.trim().isEmpty) {
      // Whitespace (mirrors Python str.isspace()).
      flush();
      if (tokens.isNotEmpty &&
          !kdata.spaceTokens.contains(tokens.last)) {
        tokens.add(nextSpace());
      }
      continue;
    }
    if (_letters.contains(ch)) {
      word.add(r);
      continue;
    }
    flush();
    if (ch == '.') {
      tokens.add(kdata.periodToken);
    } else if ('(){}'.contains(ch)) {
      tokens.add(kdata.histPunct[ch]!);
    } else if (kdata.extendedPunct.containsKey(ch)) {
      if (mode == 'experimental') {
        tokens.add(ch);
        extensions.add('punct:${kdata.extendedPunct[ch]}');
      } else {
        unsupported.add(ch);
        notes.add("'$ch' is a modern extension, rejected in strict mode");
      }
    } else if (ch == "'") {
      notes.add('apostrophe dropped (not encodable)');
      unsupported.add(ch);
    } else {
      unsupported.add(ch);
    }
  }

  flush();
  while (tokens.isNotEmpty && kdata.spaceTokens.contains(tokens.last)) {
    tokens.removeLast();
  }

  if (unsupported.isNotEmpty) {
    final uniq = unsupported.toSet().toList()..sort();
    throw CopialeError(
        'unsupported input characters (nothing was silently altered): ' +
            uniq.map((c) => "'$c'").join(', '));
  }

  return EncodeResult(
    tokens: tokens,
    text: s,
    extensions: extensions.toSet().toList()..sort(),
    unsupported: const [],
    notes: notes,
    locked: key != null,
  );
}

List<String> _splitTokens(dynamic input) {
  if (input is List<String>) return input;
  if (input is String) {
    final t = input.trim();
    if (t.isEmpty) return [];
    return t.split(RegExp(r'\s+'));
  }
  throw ArgumentError('tokens must be a String or List<String>');
}

DecodeResult decode(dynamic tokens,
    {String mode = 'experimental', String? key}) {
  final toks = _splitTokens(tokens);
  if (key != null) validateKey(key);
  if (key != null && mode == 'strict') {
    throw CopialeError('keys are a modern extension, rejected in strict mode');
  }

  final out = <String>[];
  final notes = <String>[];
  final extensions = <String>[];
  final ambiguous = <(String, String)>[];
  final unknown = <String>[];

  for (final t in toks) {
    final expansion = kdata.tokenToText[t];
    if (expansion == null) {
      if (mode == 'strict') {
        throw CopialeError("unknown cipher token: '$t'");
      }
      unknown.add(t);
      out.add('\u2039?$t?\u203a');
      continue;
    }
    if (expansion == '<REPEAT>') {
      final prev = out.isNotEmpty ? out.last : '';
      final lastCh = prev.isEmpty
          ? ''
          : String.fromCharCode(prev.runes.last).toLowerCase();
      if (prev.isNotEmpty && consonants.contains(lastCh)) {
        out.add(String.fromCharCode(prev.runes.last));
      } else {
        notes.add("':' repeat with no preceding consonant");
      }
      continue;
    }
    var exp = expansion;
    if (exp.contains('\x01')) {
      exp = exp.replaceAll('\x01', '');
    }
    out.add(exp);
    if (kdata.ambiguous.containsKey(t)) {
      ambiguous.add((t, kdata.ambiguous[t]![1]));
    }
    if (kdata.provenance(t) == 'extension') {
      extensions.add(t);
    }
  }

  var text = out.join();
  text = text.replaceAll(_spaceRuns, ' ');
  if (key != null) {
    text = lockedUnapply(text, key);
    extensions.add('locked-key');
  }
  return DecodeResult(
    text: text,
    notes: notes,
    extensions: extensions.toSet().toList()..sort(),
    ambiguous: ambiguous,
    unknown: unknown,
    locked: key != null,
  );
}
