/// German number spelling — EXTENSION (port of copiale/numbers.py).
///
/// The authentic cipher has NO documented digits; numerals are spelled out
/// as German number words before enciphering. Lossy: 2 -> zwei -> "zwei".
library;

const List<String> _ones = [
  'null', 'eins', 'zwei', 'drei', 'vier', 'fünf', 'sechs', 'sieben',
  'acht', 'neun', 'zehn', 'elf', 'zwölf', 'dreizehn', 'vierzehn',
  'fünfzehn', 'sechzehn', 'siebzehn', 'achtzehn', 'neunzehn',
];

const Map<int, String> _tens = {
  2: 'zwanzig',
  3: 'dreißig',
  4: 'vierzig',
  5: 'fünfzig',
  6: 'sechzig',
  7: 'siebzig',
  8: 'achtzig',
  9: 'neunzig',
};

String _below100(int n) {
  if (n < 20) return _ones[n];
  final t = n ~/ 10;
  final o = n % 10;
  if (o == 0) return _tens[t]!;
  final one = o == 1 ? 'ein' : _ones[o];
  return '${one}und${_tens[t]}';
}

String _below1000(int n) {
  final h = n ~/ 100;
  final r = n % 100;
  final parts = <String>[];
  if (h != 0) {
    parts.add((h == 1 ? 'ein' : _ones[h]) + 'hundert');
  }
  if (r != 0) {
    parts.add(_below100(r));
  }
  return parts.join();
}

const List<(int, String, String)> _scales = [
  (1000000000000, 'Billion', 'Billionen'),
  (1000000000, 'Milliarde', 'Milliarden'),
  (1000000, 'Million', 'Millionen'),
];

String _spell(int n) {
  if (n < 1000) return _below1000(n);
  if (n < 1000000) {
    final h = n ~/ 1000;
    final r = n % 1000;
    final head = h == 1 ? 'ein' : _below1000(h);
    return '${head}tausend${r == 0 ? '' : _below1000(r)}';
  }
  for (final s in _scales) {
    if (n >= s.$1) {
      final q = n ~/ s.$1;
      final r = n % s.$1;
      final head = q == 1 ? 'eine ${s.$2}' : '${_spell(q)} ${s.$3}';
      return head + (r == 0 ? '' : ' ${_spell(r)}');
    }
  }
  throw StateError('number too large');
}

/// Spell an integer in German. Throws StateError outside range
/// (mirrors Python ValueError).
String spellInt(int n) {
  if (n < 0) return 'minus ${spellInt(-n)}';
  if (n == 0) return 'null';
  if (n >= 1000000000000000) {
    throw StateError('number too large for German spelling (>=10^15)');
  }
  return _spell(n);
}

/// Spell a decimal string like '3.5' as 'drei Komma fünf'.
String spellDecimal(String s) {
  var neg = false;
  if (s.startsWith('+') || s.startsWith('-')) {
    neg = s[0] == '-';
    s = s.substring(1);
  }
  if (s.contains('.') || s.contains(',')) {
    final sep = s.contains('.') ? '.' : ',';
    final idx = s.indexOf(sep);
    final whole = s.substring(0, idx);
    final frac = s.substring(idx + 1);
    final w = whole.isEmpty ? 'null' : spellInt(int.parse(whole));
    final digits = frac.split('').map((c) => _ones[int.parse(c)]).join(' ');
    return '${neg ? 'minus ' : ''}$w Komma $digits';
  }
  return '${neg ? 'minus ' : ''}${spellInt(int.parse(s))}';
}
