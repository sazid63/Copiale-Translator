"""
Copiale translator: encode (English/letters -> cipher tokens) and
decode (cipher tokens -> letters).

Two modes:
  strict       - only historically documented features. Numerals and the modern
                 punctuation extensions are REJECTED (nothing is silently altered).
  experimental - additionally enables the explicitly approved extensions:
                 numerals spelled as German words, and the extended punctuation
                 tokens ( , ? ! ; = ).  Every extension use is reported.

Nothing is ever dropped silently: unsupported input raises CopialeError.
"""
from __future__ import annotations
import re
from . import key as K
from . import numbers as N


class CopialeError(Exception):
    pass


CONSONANTS = set("bcdfghjklmnpqrstvwxyzß")


# ---------------------------------------------------------------------------
# Encoding
# ---------------------------------------------------------------------------
_MULTI_SORTED = sorted(K.HIST_MULTI, key=lambda p: -len(p[0]))
_NUM_RE = re.compile(r"[+-]?\d+(?:[.,]\d+)?")


def _choose_homophone(letter, counters):
    toks = K.HIST_LETTER_HOMOPHONES[letter]
    i = counters.get(letter, 0)
    counters[letter] = i + 1
    return toks[i % len(toks)]


def _encode_word(word, counters, use_colon, unsupported):
    """word (lowercase) -> list of tokens, using greedy longest-match."""
    tokens = []
    letters = []          # parallel: produced letter(s) per token
    i = 0
    n = len(word)
    while i < n:
        matched = False
        for unit, tok in _MULTI_SORTED:
            if word.startswith(unit, i):
                tokens.append(tok)
                letters.append(unit)
                i += len(unit)
                matched = True
                break
        if matched:
            continue
        ch = word[i]
        if ch in K.HIST_LETTER_HOMOPHONES:
            tokens.append(_choose_homophone(ch, counters))
            letters.append(ch)
        else:
            unsupported.append(ch)
            tokens.append(None)
            letters.append(ch)
        i += 1

    if use_colon:
        # Replace the 2nd of an adjacent doubled consonant with ":" when the
        # previous token expands to exactly that single consonant.
        j = 1
        while j < len(tokens):
            if (letters[j] == letters[j - 1]
                    and letters[j] in CONSONANTS
                    and tokens[j] is not None
                    and len(letters[j - 1]) == 1):
                tokens[j] = K.REPEAT_TOKEN
            j += 1
    return tokens


def encode(text, *, mode="experimental", spell_numbers=True,
           number_lang="de", use_colon=True):
    """
    Returns dict(
        tokens=[...], text=normalized plaintext used, extensions=[...],
        unsupported=[...], notes=[...]
    )
    Raises CopialeError if unsupported input is present.
    """
    if mode not in ("strict", "experimental"):
        raise ValueError("mode must be 'strict' or 'experimental'")

    notes = []
    extensions = []
    unsupported = []

    s = text.lower()
    # unify some punctuation
    s = s.replace("’", "'")

    if spell_numbers and mode == "experimental":
        def repl(m):
            tok = m.group(0)
            extensions.append("numerals->german")
            if tok.lstrip("+-").startswith("."):
                return tok
            if "." in tok or "," in tok:
                return N.spell_decimal(tok)
            return N.spell_int(int(tok))
        s = _NUM_RE.sub(repl, s)
    elif re.search(r"\d", s):
        if mode == "strict":
            unsupported.extend(sorted(set(re.findall(r"\d", s))))
            notes.append("digits are not part of the historical cipher")

    counters = {}
    tokens = []
    word = []
    space_i = [0]

    def next_space():
        t = K.SPACE_CHOICES[space_i[0] % len(K.SPACE_CHOICES)]
        space_i[0] += 1
        return t

    def flush():
        if word:
            toks = _encode_word("".join(word), counters, use_colon, unsupported)
            for t in toks:
                if t is None:
                    # unsupported char already recorded; emit a visible marker
                    tokens.append("<?>")
                else:
                    tokens.append(t)
            word.clear()

    for ch in s:
        if ch.isspace():
            flush()
            if tokens and tokens[-1] not in K.SPACE_TOKENS:
                tokens.append(next_space())
            continue
        if ch in "abcdefghijklmnopqrstuvwxyzäöüß":
            word.append(ch)
            continue
        flush()
        if ch == ".":
            tokens.append(K.PERIOD_TOKEN)
        elif ch in "(){}":
            tokens.append(K.HIST_PUNCT[ch])
        elif ch in K.EXTENDED_PUNCT:
            if mode == "experimental":
                tokens.append(ch)
                extensions.append(f"punct:{K.EXTENDED_PUNCT[ch]}")
            else:
                unsupported.append(ch)
                notes.append(f"{ch!r} is a modern extension, rejected in strict mode")
        elif ch == "'":
            notes.append("apostrophe dropped (not encodable)")
            unsupported.append(ch)
        else:
            unsupported.append(ch)

    flush()
    # drop a trailing space token
    while tokens and tokens[-1] in K.SPACE_TOKENS:
        tokens.pop()

    if unsupported:
        uniq = sorted(set(unsupported))
        raise CopialeError(
            "unsupported input characters (nothing was silently altered): "
            + ", ".join(repr(c) for c in uniq)
        )

    return {
        "tokens": tokens,
        "text": s,
        "extensions": sorted(set(extensions)),
        "unsupported": [],
        "notes": notes,
    }


def render(tokens):
    return " ".join(tokens)


# ---------------------------------------------------------------------------
# Decoding
# ---------------------------------------------------------------------------
def decode(tokens, *, mode="experimental"):
    """
    tokens: list of cipher tokens (or a whitespace-separated string).
    Returns dict(text=..., notes=[...], extensions=[...], ambiguous=[...],
                 unknown=[...])
    """
    if isinstance(tokens, str):
        tokens = tokens.split()

    out = []
    notes = []
    extensions = []
    ambiguous = []
    unknown = []

    for t in tokens:
        expansion = K.TOKEN_TO_TEXT.get(t)
        if expansion is None:
            if mode == "strict":
                raise CopialeError(f"unknown cipher token: {t!r}")
            unknown.append(t)
            out.append(f"\u2039?{t}?\u203a")
            continue
        if expansion == "<REPEAT>":
            prev = out[-1] if out else ""
            if prev and prev[-1:].lower() in CONSONANTS:
                out.append(prev[-1])
            else:
                notes.append("':' repeat with no preceding consonant")
            continue
        if "\x01" in expansion:
            expansion = expansion.replace("\x01", "")
        out.append(expansion)
        if t in K.AMBIGUOUS:
            ambiguous.append((t, K.AMBIGUOUS[t][1]))
        if K.provenance(t) == "extension":
            extensions.append(t)

    text = "".join(out)
    # collapse runs of spaces introduced by NULL tokens
    text = re.sub(r"  +", " ", text)
    return {
        "text": text,
        "notes": notes,
        "extensions": sorted(set(extensions)),
        "ambiguous": ambiguous,
        "unknown": unknown,
    }
