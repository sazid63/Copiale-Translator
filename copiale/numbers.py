"""
German number spelling — EXTENSION (decision #2).

The authentic Copiale cipher has NO documented digits.  In the manuscript the
Arabic numerals, when they occur, are written in the clear (see the "Die
Algebra" document), which is a document-level exception, not part of the cipher
key.  Per the project decision, our translator spells numerals out as German
number words before enciphering.  This is a MODERN extension and is flagged as
such in every code path that uses it.

Supported: integers (with optional leading sign).  Decimals are spelled with
"Komma".  Fractions are NOT supported (flagged as unsupported).
"""

_ONES = ["null", "eins", "zwei", "drei", "vier", "fünf", "sechs", "sieben",
         "acht", "neun", "zehn", "elf", "zwölf", "dreizehn", "vierzehn",
         "fünfzehn", "sechzehn", "siebzehn", "achtzehn", "neunzehn"]
_TENS = {2: "zwanzig", 3: "dreißig", 4: "vierzig", 5: "fünfzig",
         6: "sechzig", 7: "siebzig", 8: "achtzig", 9: "neunzig"}


def _below_100(n):
    if n < 20:
        return _ONES[n]
    t, o = divmod(n, 10)
    if o == 0:
        return _TENS[t]
    # German: ones + "und" + tens, e.g. 21 = einundzwanzig
    one = "ein" if o == 1 else _ONES[o]
    return f"{one}und{_TENS[t]}"


def _below_1000(n):
    h, r = divmod(n, 100)
    parts = []
    if h:
        parts.append(("ein" if h == 1 else _ONES[h]) + "hundert")
    if r:
        parts.append(_below_100(r))
    return "".join(parts)


_SCALES = [
    (10 ** 12, "Billion", "Billionen"),
    (10 ** 9, "Milliarde", "Milliarden"),
    (10 ** 6, "Million", "Millionen"),
]


def _spell(n):
    if n < 1000:
        return _below_1000(n)
    if n < 10 ** 6:
        h, r = divmod(n, 1000)
        head = "ein" if h == 1 else _below_1000(h)
        return head + "tausend" + ("" if r == 0 else _below_1000(r))
    for size, sing, plur in _SCALES:
        if n >= size:
            q, r = divmod(n, size)
            head = ("eine " + sing) if q == 1 else (_spell(q) + " " + plur)
            return head + ("" if r == 0 else " " + _spell(r))
    raise ValueError("number too large")


def spell_int(n):
    """Spell an integer in German. Raises ValueError outside range."""
    if n < 0:
        return "minus " + spell_int(-n)
    if n == 0:
        return "null"
    if n >= 10 ** 15:
        raise ValueError("number too large for German spelling (>=10^15)")
    return _spell(n)


def spell_decimal(s):
    """Spell a decimal string like '3.5' as 'drei Komma fünf'."""
    neg = False
    if s[:1] in "+-":
        neg = s[0] == "-"
        s = s[1:]
    if "." in s:
        whole, frac = s.split(".", 1)
    elif "," in s:
        whole, frac = s.split(",", 1)
    else:
        return ("minus " if neg else "") + spell_int(int(s))
    w = spell_int(int(whole)) if whole not in ("",) else "null"
    digits = " ".join(_ONES[int(c)] for c in frac)
    return ("minus " if neg else "") + f"{w} Komma {digits}"
