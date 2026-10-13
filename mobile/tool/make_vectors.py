"""Regenerate mobile/test/test_vectors.json from the reference Python
implementation. Run from the research repo root:

    python /path/to/mobile/tool/make_vectors.py <research-root> <out-json>

The Dart test suite (mobile/test/cipher_test.dart) loads this file and must
reproduce every vector exactly — that is what guarantees keys interoperate
between the app and the Python translator.
"""
import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])
OUT = Path(sys.argv[2])
sys.path.insert(0, str(ROOT))

from copiale import encode, decode  # noqa: E402
from copiale import locked as L  # noqa: E402

KEYS = [
    "test-key-123",
    "my-secret-key",
    "a",
    "Z",
    "correct horse battery staple",
    "schlüssel 🔑",
]

LOCKED_SAMPLES = [
    ("my-secret-key", "meet at midnight"),
    ("test-key-123", "the secret master of the lodge"),
    ("test-key-123", "hello world"),
    ("correct horse battery staple", "bitter alle sonne mutter"),
    ("Z", "add 2 and 3"),
    ("a", "straße grüße"),
    ("schlüssel 🔑", "ready? go!"),
]

PLAIN_SAMPLES = [
    "ok",
    "hello world",
    "schule",
    "the quick brown fox jumps over the lazy dog",
    "add 2 and 3",
    "the oculist opens the book",
]


def main():
    assert L.DERIVATION == "Copiale-Lock-v2", L.DERIVATION
    vectors = {
        "derivation": L.DERIVATION,
        "alphabet": L.ALPHABET,
        "permutations": [
            {"key": k, "permutation": L.permutation(k)} for k in KEYS
        ],
        "locked": [],
        "plain": [],
    }
    for key, text in LOCKED_SAMPLES:
        toks = encode(text, key=key)["tokens"]
        back = decode(toks, key=key)["text"]
        vectors["locked"].append({
            "key": key,
            "plaintext": text,
            "tokens": toks,
            "decoded": back,
        })
    for text in PLAIN_SAMPLES:
        toks = encode(text)["tokens"]
        vectors["plain"].append({
            "plaintext": text,
            "tokens": toks,
            "decoded": decode(toks)["text"],
        })
    OUT.write_text(json.dumps(vectors, ensure_ascii=True, indent=1) + "\n",
                   encoding="utf-8")
    print(f"wrote {OUT} "
          f"({len(vectors['permutations'])} perms, "
          f"{len(vectors['locked'])} locked, "
          f"{len(vectors['plain'])} plain)")


if __name__ == "__main__":
    main()
