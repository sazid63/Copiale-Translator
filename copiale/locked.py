"""
Optional user-key layer for the Copiale translator (modern extension, E6).

This module is NOT historical. It adds an extra letter-substitution step,
derived deterministically from a user-supplied passphrase, that runs *inside*
the normal encode/decode pipeline:

  encode with key:  plaintext -> substitute letters -> cipher tokens
  decode with key:  cipher tokens -> substituted text -> inverse substitute

Because the substitution happens at the letter level, the emitted tokens are
still ordinary historical cipher tokens. Decoding the same tokens *without*
the key yields the substituted (unreadable) text instead of the message.

Derivation ("Copiale-Lock-v2", portable across languages): the permutation of
the 29-letter alphabet is produced by a Fisher-Yates shuffle driven by a
SHA-256 counter stream. Block c = SHA256(b"Copiale-Lock-v2" + b"\\x00" +
key_utf8 + counter_be32), consumed as consecutive big-endian uint32 words;
each position i (n-1 down to 1) takes j = randbelow(i+1) with rejection
sampling (k = bit_length(limit-1) top bits of the next word). Any language
with SHA-256 can reproduce it exactly — this is what the mobile app does.

ß is normalised to "ss" before substitution (the same documented rule as
unlocked mode); everything else round-trips exactly.

Approval: implemented at the project owner's written request; recorded as E6
in spec/extensions.md. Rejected in strict mode.
"""
from __future__ import annotations
import hashlib
import re
import secrets
import string

# Letters covered by the substitution. ß is excluded: a ß encodes to a token
# that decodes as TWO characters ("ss"), so it can never survive a
# character-level inverse. Locked mode normalises ß to "ss" first — exactly
# the documented historical rule.
ALPHABET = "abcdefghijklmnopqrstuvwxyzäöü"

# Derivation version tag (domain separation). Bump if the derivation changes.
DERIVATION = "Copiale-Lock-v2"

_KEYGEN_ALPHABET = string.ascii_letters + string.digits
DEFAULT_KEY_LENGTH = 16
MIN_KEY_LENGTH = 4
MAX_KEY_LENGTH = 128


def validate_key(key):
    """Return the key if usable, else raise ValueError."""
    if not isinstance(key, str) or not key.strip():
        raise ValueError("key must be a non-empty string")
    return key


def _words(key):
    """Infinite stream of uint32 words (big-endian) from the SHA-256 counter
    stream. Portable: any SHA-256 implementation reproduces it."""
    kb = validate_key(key).encode("utf-8")
    counter = 0
    while True:
        block = hashlib.sha256(
            DERIVATION.encode("ascii") + b"\x00" + kb
            + counter.to_bytes(4, "big")
        ).digest()
        for i in range(0, 32, 4):
            yield int.from_bytes(block[i:i + 4], "big")
        counter += 1


def permutation(key):
    """Deterministic permutation of ALPHABET derived from key."""
    validate_key(key)
    perm = list(ALPHABET)
    stream = _words(key)
    for i in range(len(perm) - 1, 0, -1):
        limit = i + 1
        k = (limit - 1).bit_length()
        while True:
            cand = next(stream) >> (32 - k)
            if cand < limit:
                break
        perm[i], perm[cand] = perm[cand], perm[i]
    return "".join(perm)


def apply(text, key):
    """Substitute every alphabet letter of text using key. Case of the
    caller is expected to be already lowered (encode() lowercases first)."""
    perm = permutation(key)
    return text.translate(str.maketrans(ALPHABET, perm))


# Spans that must survive inverse substitution untouched: logogram markers
# (*star*) and unknown-token markers (< ?tok? >) produced by the decoder.
_PROTECTED = re.compile(r"(\*[^*]*\*|‹[^›]*›)")


def unapply(text, key):
    """Inverse of apply(), leaving *...* and < ?...? > spans intact."""
    perm = permutation(key)
    table = str.maketrans(perm, ALPHABET)
    parts = _PROTECTED.split(text)
    for i in range(0, len(parts), 2):
        parts[i] = parts[i].translate(table)
    return "".join(parts)


def generate_key(length=DEFAULT_KEY_LENGTH):
    """Generate a random shareable key (ASCII letters + digits)."""
    if not isinstance(length, int) or not (MIN_KEY_LENGTH <= length <= MAX_KEY_LENGTH):
        raise ValueError(
            f"key length must be an integer between {MIN_KEY_LENGTH} "
            f"and {MAX_KEY_LENGTH}"
        )
    return "".join(secrets.choice(_KEYGEN_ALPHABET) for _ in range(length))
