"""
Copiale cipher — verified symbol key.

Provenance tags:
  "historical"  - documented in Knight/Megyesi/Schaefer (2011) Figure 6 / Figure 2,
                  and independently re-verified here against the published
                  Stockholm University transcription <-> decipherment pair
                  (99.8% letter agreement, see tools/verify_corpus.py).
  "convention"  - a deterministic choice among historically free alternatives
                  (homophone selection, ambiguity resolution). Not new symbols.
  "extension"   - a MODERN addition, approved by the project owner. Must never be
                  presented as historical.

The cipher is a homophonic substitution over a German-style alphabet.  Plain
"unaccented Roman letters" act as WORD SPACES.  A handful of symbols act as
LOG OGRAMS (whole concepts, not letters).
"""

# ---------------------------------------------------------------------------
# 1. Historical letter homophones  (plaintext letter -> cipher tokens)
#    Verified against Fig. 6 and the SU transcription/decipherment corpus.
# ---------------------------------------------------------------------------
HIST_LETTER_HOMOPHONES = {
    "a": ["p.", "n.", "h."],
    "ä": ["fem"],
    "b": ["sqp"],
    "c": ["bas"],
    "d": ["pi", "z"],
    "e": ["ah", "eh", "ih", "oh", "uh", "grr", "zzz"],
    "f": ["sqi"],
    "g": ["del", "x."],
    "h": ["hd"],
    "i": ["y..", "ns", "iot"],
    "j": ["car"],
    "k": ["gam"],
    "l": ["c."],
    "m": ["plus"],
    "n": ["mu", "ru", "nu", "g"],
    "o": ["tri", "o."],
    "ö": ["no"],
    "p": ["d"],
    "q": ["qua"],
    "r": ["r.", "three", "j"],
    "s": ["bar"],
    "ß": ["grc"],            # ß is written "ss" -> [  (SS)
    "t": ["lam"],
    "u": ["ni", "ki"],
    "ü": ["grl"],
    "v": ["mal"],
    "w": ["m."],
    "x": ["pipe"],
    "y": ["inf"],
    "z": ["s."],
}

# Multi-letter plaintext units -> single cipher token (longest match first).
HIST_MULTI = [
    ("sch", "cross"),   # Fig.6: SCH -> T
    ("ch", "arr"),      # Fig.6: CH  -> /
    ("ss", "grc"),      # Fig.6: SS  -> [
    ("st", "hk"),       # Fig.6: ST  -> 7
    ("en", "uu"),       # Fig.6: EN/EM -> G
]

# The ":" token doubles the previous consonant (Fig.6).
REPEAT_TOKEN = ":"

# Plain period glyph (Fig. 2:  . -> . )
PERIOD_TOKEN = "."

# ---------------------------------------------------------------------------
# 2. Word-space tokens  (unaccented Roman letters + fancy/underlined forms)
#    Fig.6 "space" row + verified empirically.
# ---------------------------------------------------------------------------
SPACE_TOKENS = set("abcefhiklmnopqrstuvwxy") | {"ds", "gs", "zs", "ft", "longs"}
# Deterministic, documented order for homophonic space selection (decision #4).
SPACE_CHOICES = ("a", "b", "c", "e", "f", "h", "i", "k", "l", "m", "n", "o",
                 "p", "q", "r", "s", "t", "u", "v", "w", "x", "y",
                 "ds", "gs", "zs", "ft", "longs")

# ---------------------------------------------------------------------------
# 3. Null / formatting tokens (paragraph capitals & layout marks) -> produce ""
# ---------------------------------------------------------------------------
NULL_TOKENS = (
    set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    | {'"', "...", "..", "....", ".....", "......", ".......",
       "%%", "%%%", "%%%%", "%%%%%", "@@@@@", "*krussedull*",
       "/Copiales", "3.", "ZS", "", "(A-H", "()"}
)

# ---------------------------------------------------------------------------
# 4. Logograms (whole-concept symbols).  Shown using the published decipherment
#    notation.  These are historical.
# ---------------------------------------------------------------------------
LOGO_TOKENS = {
    "o..": "*o*",        # society
    "star": "*star*",    # secret
    "nee": "*nee*",      # master
    "tri..": "*tri..*",  # lodge
    "bigx": "*bigx*",    # freemason
    "gate": "*gate*",    # table-shaped (gate)
    "lip": "*lip*",      # oculist / eye
    "bigl": "*bigl*",    # position of feet
    "tribig": "*tribig*",  # lodge
    "sci": "*sci*",      # "God"
    "toe": "*toe*",      # power
    "gat": "*gat*",      # gate symbol (¬)
}

# ---------------------------------------------------------------------------
# 5. Approved modern EXTENSIONS (NOT historical)
# ---------------------------------------------------------------------------
EXTENDED_PUNCT = {
    ",": "comma",
    "?": "question mark",
    "!": "exclamation mark",
    ";": "statement separator",
    "=": "equals",
}
# Characters mapped historically as punctuation by the manuscript itself:
HIST_PUNCT = {".": ".", "(": "smil", ")": "smir", "{": "{", "}": "}"}
# token -> literal char produced
HIST_PUNCT_TOKEN = {".": ".", "smil": "(", "smir": ")", "{": "{", "}": "}"}


def build_token_to_text():
    """token -> produced text (for the decoder)."""
    out = {}
    for letter, toks in HIST_LETTER_HOMOPHONES.items():
        for t in toks:
            out[t] = letter
    for unit, t in HIST_MULTI:
        out[t] = unit
    for t in SPACE_TOKENS:
        out[t] = " "
    for t in NULL_TOKENS:
        out.setdefault(t, "")
    for t, disp in LOGO_TOKENS.items():
        out[t] = "\x01" + disp + "\x01"     # placeholder sentinel
    for t, ch in HIST_PUNCT_TOKEN.items():
        out[t] = ch
    for ch in EXTENDED_PUNCT:
        out[ch] = ch
    out[REPEAT_TOKEN] = "<REPEAT>"
    return out


TOKEN_TO_TEXT = build_token_to_text()


def provenance(token):
    if token in EXTENDED_PUNCT:
        return "extension"
    if token in LOGO_TOKENS or token in NULL_TOKENS or token in SPACE_TOKENS:
        return "historical"
    if token in HIST_PUNCT_TOKEN:
        return "historical"
    if token in TOKEN_TO_TEXT:
        return "historical"
    return "unknown"


# Historically ambiguous tokens and the deterministic resolution we adopt.
AMBIGUOUS = {
    "grc": ("ss", "S or SS -> we always read SS"),
    "gam": ("k", "H or K -> we always read K"),
    "uu": ("en", "EN or EM -> we always read EN"),
}
