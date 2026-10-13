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

ß is normalised to "ss" before substitution (the same documented rule as
unlocked mode); everything else round-trips exactly.

Approval: implemented at the project owner's written request; recorded as E6
in spec/extensions.md. Rejected in strict mode.
"""
from __future__ import annotations
import hashlib
import random
import re
import secrets
import string

# Letters covered by the substitution (the encoder's letter alphabet minus
# ß: a ß encodes to a token that decodes as TWO characters ("ss"), so it can
# never survive a character-level inverse. Locked mode normalises ß to "ss"
# first — exactly the documented historical rule — and substitutes the rest.
ALPHABET = "abcdefghijklmnopqrstuvwxyzäöü"

_KEYGEN_ALPHABET = string.ascii_letters + string.digits
DEFAULT_KEY_LENGTH = 16
MIN_KEY_LENGTH = 4
MAX_KEY_LENGTH = 128


def validate_key(key):
    """Return the key if usable, else raise ValueError."""
    if not isinstance(key, str) or not key.strip():
        raise ValueError("key must be a non-empty string")
    return key


def _seed(key):
    return int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest(), "big")


def permutation(key):
    """Deterministic permutation of ALPHABET derived from key."""
    validate_key(key)
    rng = random.Random(_seed(key))
    perm = list(ALPHABET)
    rng.shuffle(perm)
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
