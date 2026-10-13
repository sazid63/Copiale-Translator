"""Tests for the optional user-key layer (modern extension E6)."""
import contextlib
import io
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from copiale import encode, decode, CopialeError
from copiale import locked as L
from copiale import key as K
from copiale.cli import main as cli_main

KEY = "test-key-123"
OTHER_KEY = "different-key-456"


class TestLockedRoundTrip(unittest.TestCase):
    def test_basic_roundtrip(self):
        for s in ["ok", "hello world", "the secret master of the lodge",
                  "meet at midnight", "bitter alle sonne",
                  "schule chor kirche"]:
            toks = encode(s, key=KEY)["tokens"]
            self.assertEqual(decode(toks, key=KEY)["text"], s, s)

    def test_umlaut_and_sz(self):
        # ß normalises to ss first (same documented rule as unlocked mode).
        toks = encode("straße grüße", key=KEY)["tokens"]
        self.assertEqual(decode(toks, key=KEY)["text"], "strasse grüsse")
        self.assertEqual(decode(toks, key=KEY)["text"],
                         decode(encode("straße grüße")["tokens"])["text"])

    def test_numbers_covered(self):
        # number words are spelled out first, then substituted: no leak,
        # and the letter-level round-trip restores the spelled form.
        toks = encode("add 2 and 3", key=KEY)["tokens"]
        self.assertEqual(decode(toks, key=KEY)["text"], "add zwei and drei")

    def test_colon_repeat_with_key(self):
        # Craft input whose substituted form is exactly "bitter", so the
        # doubled-t ":" path fires deterministically whatever the key is.
        plain = L.unapply("bitter", KEY)
        toks = encode(plain, key=KEY)["tokens"]
        self.assertIn(":", toks)
        self.assertEqual(decode(toks, key=KEY)["text"], plain)

    def test_locked_tokens_are_valid_cipher(self):
        toks = encode("hello world", key=KEY)["tokens"]
        for t in toks:
            self.assertIn(t, K.TOKEN_TO_TEXT, t)

    def test_deterministic(self):
        self.assertEqual(encode("hello", key=KEY)["tokens"],
                         encode("hello", key=KEY)["tokens"])

    def test_different_keys_differ(self):
        self.assertNotEqual(encode("hello", key=KEY)["tokens"],
                            encode("hello", key=OTHER_KEY)["tokens"])

    def test_reported_as_extension(self):
        r = encode("hi", key=KEY)
        self.assertTrue(r["locked"])
        self.assertIn("locked-key", r["extensions"])
        r2 = decode(encode("hi", key=KEY)["tokens"], key=KEY)
        self.assertTrue(r2["locked"])
        self.assertIn("locked-key", r2["extensions"])
        self.assertFalse(encode("hi")["locked"])
        self.assertFalse(decode(encode("hi")["tokens"])["locked"])


class TestLockedSecrecy(unittest.TestCase):
    def test_no_key_gives_gibberish(self):
        s = "the secret master of the lodge"
        toks = encode(s, key=KEY)["tokens"]
        self.assertNotEqual(decode(toks)["text"], s)

    def test_wrong_key_gives_gibberish(self):
        s = "the secret master of the lodge"
        toks = encode(s, key=KEY)["tokens"]
        self.assertNotEqual(decode(toks, key=OTHER_KEY)["text"], s)

    def test_logogram_markers_survive(self):
        self.assertEqual(decode(["star"], key=KEY)["text"], "*star*")


class TestLockedModes(unittest.TestCase):
    def test_strict_rejects_key(self):
        with self.assertRaises(CopialeError):
            encode("hi", mode="strict", key=KEY)
        with self.assertRaises(CopialeError):
            decode(["hd"], mode="strict", key=KEY)

    def test_empty_key_rejected(self):
        for bad in ["", "   "]:
            with self.assertRaises(CopialeError):
                encode("hi", key=bad)
            with self.assertRaises(CopialeError):
                decode(["hd"], key=bad)

    def test_no_key_behaviour_unchanged(self):
        self.assertEqual(decode(["tri", "gam"])["text"], "ok")
        r = encode("ok")
        self.assertEqual(decode(r["tokens"])["text"], "ok")


class TestKeygen(unittest.TestCase):
    def test_length_and_charset(self):
        import string
        allowed = set(string.ascii_letters + string.digits)
        for n in (4, 8, 16, 32):
            k = L.generate_key(n)
            self.assertEqual(len(k), n)
            self.assertTrue(set(k) <= allowed, k)

    def test_unique(self):
        self.assertNotEqual(L.generate_key(), L.generate_key())

    def test_bad_length(self):
        for bad in (0, 3, 129, -1, "16", None):
            with self.assertRaises(ValueError):
                L.generate_key(bad)


class TestLockedCLI(unittest.TestCase):
    def _run(self, argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = cli_main(argv)
        self.assertEqual(rc, 0)
        return out.getvalue().strip()

    def test_cli_key_roundtrip(self):
        toks = self._run(["encode", "meet at midnight", "--key", KEY])
        self.assertEqual(self._run(["decode", toks, "--key", KEY]),
                         "meet at midnight")

    def test_cli_keygen(self):
        k = self._run(["keygen", "--length", "8"])
        self.assertEqual(len(k), 8)


if __name__ == "__main__":
    unittest.main(verbosity=2)
