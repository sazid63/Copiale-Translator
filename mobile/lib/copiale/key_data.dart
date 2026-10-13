/// Copiale cipher — verified symbol key (port of copiale/key.py).
///
/// Provenance: "historical" = Knight/Megyesi/Schaefer (2011);
/// "convention" = deterministic choice among free alternatives;
/// "extension" = MODERN addition, never to be presented as historical.
library;

// 1. Historical letter homophones (plaintext letter -> cipher tokens).
const Map<String, List<String>> histLetterHomophones = {
  'a': ['p.', 'n.', 'h.'],
  'ä': ['fem'],
  'b': ['sqp'],
  'c': ['bas'],
  'd': ['pi', 'z'],
  'e': ['ah', 'eh', 'ih', 'oh', 'uh', 'grr', 'zzz'],
  'f': ['sqi'],
  'g': ['del', 'x.'],
  'h': ['hd'],
  'i': ['y..', 'ns', 'iot'],
  'j': ['car'],
  'k': ['gam'],
  'l': ['c.'],
  'm': ['plus'],
  'n': ['mu', 'ru', 'nu', 'g'],
  'o': ['tri', 'o.'],
  'ö': ['no'],
  'p': ['d'],
  'q': ['qua'],
  'r': ['r.', 'three', 'j'],
  's': ['bar'],
  'ß': ['grc'],
  't': ['lam'],
  'u': ['ni', 'ki'],
  'ü': ['grl'],
  'v': ['mal'],
  'w': ['m.'],
  'x': ['pipe'],
  'y': ['inf'],
  'z': ['s.'],
};

// Multi-letter plaintext units -> single cipher token (longest match first).
// Order matches the Python reference (stable sort by descending length).
const List<String> histMultiUnits = ['sch', 'ch', 'ss', 'st', 'en'];
const List<String> histMultiTokens = ['cross', 'arr', 'grc', 'hk', 'uu'];

// The ":" token doubles the previous consonant.
const String repeatToken = ':';

// Plain period glyph.
const String periodToken = '.';

// 2. Word-space tokens.
const Set<String> spaceTokens = {
  'a', 'b', 'c', 'e', 'f', 'h', 'i', 'k', 'l', 'm', 'n', 'o',
  'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y',
  'ds', 'gs', 'zs', 'ft', 'longs',
};

// Deterministic, documented order for homophonic space selection.
const List<String> spaceChoices = [
  'a', 'b', 'c', 'e', 'f', 'h', 'i', 'k', 'l', 'm', 'n', 'o',
  'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y',
  'ds', 'gs', 'zs', 'ft', 'longs',
];

// 3. Null / formatting tokens -> produce "".
final Set<String> nullTokens = {
  ...'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split(''),
  '"', '...', '..', '....', '.....', '......', '.......',
  '%%', '%%%', '%%%%', '%%%%%', '@@@@@', '*krussedull*',
  '/Copiales', '3.', 'ZS', '', '(A-H', '()',
};

// 4. Logograms (whole-concept symbols, historical).
const Map<String, String> logoTokens = {
  'o..': '*o*',
  'star': '*star*',
  'nee': '*nee*',
  'tri..': '*tri..*',
  'bigx': '*bigx*',
  'gate': '*gate*',
  'lip': '*lip*',
  'bigl': '*bigl*',
  'tribig': '*tribig*',
  'sci': '*sci*',
  'toe': '*toe*',
  'gat': '*gat*',
};

// 5. Approved modern EXTENSIONS (NOT historical).
const Map<String, String> extendedPunct = {
  ',': 'comma',
  '?': 'question mark',
  '!': 'exclamation mark',
  ';': 'statement separator',
  '=': 'equals',
};

// Characters mapped historically as punctuation by the manuscript itself.
const Map<String, String> histPunct = {
  '.': '.',
  '(': 'smil',
  ')': 'smir',
  '{': '{',
  '}': '}',
};

// Token -> literal char produced.
const Map<String, String> histPunctToken = {
  '.': '.',
  'smil': '(',
  'smir': ')',
  '{': '{',
  '}': '}',
};

/// Token -> produced text (for the decoder). Mirrors build_token_to_text().
final Map<String, String> tokenToText = _buildTokenToText();

Map<String, String> _buildTokenToText() {
  final out = <String, String>{};
  histLetterHomophones.forEach((letter, toks) {
    for (final t in toks) {
      out[t] = letter;
    }
  });
  for (var i = 0; i < histMultiUnits.length; i++) {
    out[histMultiTokens[i]] = histMultiUnits[i];
  }
  for (final t in spaceTokens) {
    out[t] = ' ';
  }
  for (final t in nullTokens) {
    out.putIfAbsent(t, () => '');
  }
  logoTokens.forEach((t, disp) {
    out[t] = '\x01$disp\x01';
  });
  histPunctToken.forEach((t, ch) {
    out[t] = ch;
  });
  for (final ch in extendedPunct.keys) {
    out[ch] = ch;
  }
  out[repeatToken] = '<REPEAT>';
  return out;
}

String provenance(String token) {
  if (extendedPunct.containsKey(token)) return 'extension';
  if (logoTokens.containsKey(token) ||
      nullTokens.contains(token) ||
      spaceTokens.contains(token)) {
    return 'historical';
  }
  if (histPunctToken.containsKey(token)) return 'historical';
  if (tokenToText.containsKey(token)) return 'historical';
  return 'unknown';
}

// Historically ambiguous tokens and the deterministic resolution we adopt.
const Map<String, List<String>> ambiguous = {
  'grc': ['ss', 'S or SS -> we always read SS'],
  'gam': ['k', 'H or K -> we always read K'],
  'uu': ['en', 'EN or EM -> we always read EN'],
};
