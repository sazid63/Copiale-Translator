"""Command-line interface for the Copiale translator.

Usage:
  python -m copiale.cli encode "text"     [--strict] [--key KEY | --new-key]
  python -m copiale.cli decode "a b c"    [--strict] [--key KEY]
  python -m copiale.cli roundtrip "text"  [--key KEY]
  python -m copiale.cli keygen            [--length N]
  python -m copiale.cli symbols
  python -m copiale.cli selftest

Locked (keyed) mode is an optional modern extension: encode with a key,
share the tokens AND the key with the recipient, who decodes with the same
key. Without the key the translator behaves exactly as before.
"""
import sys
import argparse
from . import encode, decode, render, CopialeError
from . import key as K
from .locked import generate_key, unapply


def main(argv=None):
    p = argparse.ArgumentParser(prog="copiale", description="Copiale cipher translator")
    sub = p.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("encode", help="plaintext -> cipher tokens")
    e.add_argument("text")
    e.add_argument("--strict", action="store_true")
    e.add_argument("--key", metavar="KEY", default=None,
                   help="optional passphrase: lock the message with this key")
    e.add_argument("--new-key", action="store_true",
                   help="generate a fresh key, lock with it, and print it")

    d = sub.add_parser("decode", help="cipher tokens -> plaintext")
    d.add_argument("text")
    d.add_argument("--strict", action="store_true")
    d.add_argument("--key", metavar="KEY", default=None,
                   help="the key the message was locked with")

    r = sub.add_parser("roundtrip", help="encode then decode")
    r.add_argument("text")
    r.add_argument("--key", metavar="KEY", default=None,
                   help="optional passphrase for a locked round-trip")

    kg = sub.add_parser("keygen", help="generate a random shareable key")
    kg.add_argument("--length", type=int, default=16,
                    help="key length, 4-128 (default 16)")

    sub.add_parser("symbols", help="list the symbol inventory")
    sub.add_parser("selftest", help="run a quick built-in round-trip check")

    a = p.parse_args(argv)
    mode = "experimental"

    if a.cmd == "encode":
        if a.strict:
            mode = "strict"
        if a.key and a.new_key:
            print("ERROR: use either --key or --new-key, not both", file=sys.stderr)
            return 2
        key = a.key
        if a.new_key:
            if a.strict:
                print("ERROR: keys are a modern extension, rejected in strict mode",
                      file=sys.stderr)
                return 2
            key = generate_key()
        try:
            res = encode(a.text, mode=mode, key=key)
        except CopialeError as ex:
            print(f"ERROR: {ex}", file=sys.stderr)
            return 2
        print(render(res["tokens"]))
        if a.new_key:
            print(f"# new key: {key} (share it with the recipient along "
                  f"with the tokens)", file=sys.stderr)
        if res["extensions"]:
            print(f"# extensions used: {', '.join(res['extensions'])}", file=sys.stderr)
        for n in res["notes"]:
            print(f"# note: {n}", file=sys.stderr)
        return 0

    if a.cmd == "decode":
        if a.strict:
            mode = "strict"
        try:
            res = decode(a.text, mode=mode, key=a.key)
        except CopialeError as ex:
            print(f"ERROR: {ex}", file=sys.stderr)
            return 2
        print(res["text"])
        if res["ambiguous"]:
            for t, why in res["ambiguous"]:
                print(f"# ambiguity: {t!r} -> {why}", file=sys.stderr)
        if res["extensions"]:
            print(f"# extensions used: {', '.join(res['extensions'])}", file=sys.stderr)
        for n in res["notes"]:
            print(f"# note: {n}", file=sys.stderr)
        return 0

    if a.cmd == "roundtrip":
        res = encode(a.text, key=a.key)
        dec = decode(res["tokens"], key=a.key)
        # res["text"] is post-substitution; compare against the original
        # (pre-substitution) text so locked round-trips report correctly.
        expected = unapply(res["text"], a.key) if a.key else res["text"]
        ok = dec["text"] == expected
        print("tokens :", render(res["tokens"]))
        print("decoded:", dec["text"])
        print("input  :", expected)
        print("MATCH" if ok else "MISMATCH")
        return 0 if ok else 1

    if a.cmd == "keygen":
        try:
            print(generate_key(a.length))
        except ValueError as ex:
            print(f"ERROR: {ex}", file=sys.stderr)
            return 2
        return 0

    if a.cmd == "symbols":
        for letter in sorted(K.HIST_LETTER_HOMOPHONES):
            toks = " ".join(K.HIST_LETTER_HOMOPHONES[letter])
            print(f"{letter!r:>4} -> {toks}")
        print("multi      ->", " ".join(f"{u}={t}" for u, t in K.HIST_MULTI))
        print("logograms  ->", " ".join(f"{t}={d}" for t, d in K.LOGO_TOKENS.items()))
        print("spaces     ->", " ".join(K.SPACE_CHOICES))
        print("extensions ->", " ".join(f"{c!r}({n})" for c, n in K.EXTENDED_PUNCT.items()))
        return 0

    if a.cmd == "selftest":
        samples = [
            "the secret master of the lodge",
            "add two and three",
            "go to the table",
            "the oculist opens the book",
        ]
        bad = 0
        for s in samples:
            res = encode(s)
            dec = decode(res["tokens"])["text"]
            ok = dec == s
            bad += 0 if ok else 1
            print(f"[{'ok' if ok else 'FAIL'}] {s!r} -> {dec!r}")
        return 1 if bad else 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
