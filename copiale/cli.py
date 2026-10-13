"""Command-line interface for the Copiale translator.

Usage:
  python -m copiale.cli encode "text"     [--strict]
  python -m copiale.cli decode "a b c"    [--strict]
  python -m copiale.cli roundtrip "text"
  python -m copiale.cli symbols
  python -m copiale.cli selftest
"""
import sys
import argparse
from . import encode, decode, render, CopialeError
from . import key as K


def main(argv=None):
    p = argparse.ArgumentParser(prog="copiale", description="Copiale cipher translator")
    sub = p.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("encode", help="plaintext -> cipher tokens")
    e.add_argument("text")
    e.add_argument("--strict", action="store_true")

    d = sub.add_parser("decode", help="cipher tokens -> plaintext")
    d.add_argument("text")
    d.add_argument("--strict", action="store_true")

    r = sub.add_parser("roundtrip", help="encode then decode")
    r.add_argument("text")

    sub.add_parser("symbols", help="list the symbol inventory")
    sub.add_parser("selftest", help="run a quick built-in round-trip check")

    a = p.parse_args(argv)
    mode = "experimental"

    if a.cmd == "encode":
        if a.strict:
            mode = "strict"
        try:
            res = encode(a.text, mode=mode)
        except CopialeError as ex:
            print(f"ERROR: {ex}", file=sys.stderr)
            return 2
        print(render(res["tokens"]))
        if res["extensions"]:
            print(f"# extensions used: {', '.join(res['extensions'])}", file=sys.stderr)
        for n in res["notes"]:
            print(f"# note: {n}", file=sys.stderr)
        return 0

    if a.cmd == "decode":
        if a.strict:
            mode = "strict"
        try:
            res = decode(a.text, mode=mode)
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
        res = encode(a.text)
        dec = decode(res["tokens"])
        ok = dec["text"] == res["text"]
        print("tokens :", render(res["tokens"]))
        print("decoded:", dec["text"])
        print("input  :", res["text"])
        print("MATCH" if ok else "MISMATCH")
        return 0 if ok else 1

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
