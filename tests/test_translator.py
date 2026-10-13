"""Unit tests for the Copiale translator."""
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from copiale import encode, decode, render, CopialeError
from copiale import key as K
from copiale import numbers as N


class TestKeyIntegrity(unittest.TestCase):
    def test_no_letter_token_collision(self):
        owner = {}
        for letter, toks in K.HIST_LETTER_HOMOPHONES.items():
            for t in toks:
                self.assertNotIn(t, owner,
                                 f"token {t!r} maps to both {owner.get(t)!r} and {letter!r}")
                owner[t] = letter

    def test_every_homophone_decodes_to_its_letter(self):
        for letter, toks in K.HIST_LETTER_HOMOPHONES.items():
            for t in toks:
                got = decode([t])["text"]
                # 'ß' is normalised to 'ss' historically
                expected = "ss" if letter == "ß" else letter
                self.assertEqual(got, expected, f"{t!r} should decode to {expected!r}")

    def test_provenance_tags(self):
        self.assertEqual(K.provenance("p."), "historical")
        self.assertEqual(K.provenance(","), "extension")
        self.assertEqual(K.provenance("lip"), "historical")


class TestRoundTrip(unittest.TestCase):
    def test_all_letters(self):
        alphabet = "abcdefghijklmnopqrstuvwxyzäöü"
        for ch in alphabet:
            r = encode(ch)
            self.assertEqual(decode(r["tokens"])["text"], ch, ch)

    def test_umlaut_sz(self):
        # ß is historically written ss -> decodes as ss
        r = encode("straße")
        self.assertEqual(decode(r["tokens"])["text"], "strasse")

    def test_digraphs(self):
        for word in ["schule", "chor", "essen", "stadt", "energie", "kirche"]:
            r = encode(word)
            self.assertEqual(decode(r["tokens"])["text"], word, word)

    def test_doubled_consonants(self):
        for word in ["bitter", "alle", "sonne", "mutter", "wasser", "treffen"]:
            r = encode(word)
            self.assertEqual(decode(r["tokens"])["text"], word, word)

    def test_sentences(self):
        for s in [
            "the secret master of the lodge",
            "go to the table and wait",
            "the oculist opens the book",
            "select the third item from the list",
            "if the door is open then enter",
            "do not speak the secret word",
            "first add two and then subtract one",
        ]:
            r = encode(s)
            self.assertEqual(decode(r["tokens"])["text"], s, s)

    def test_deterministic(self):
        s = "the quick brown fox jumps over the lazy dog"
        a = encode(s)["tokens"]
        b = encode(s)["tokens"]
        self.assertEqual(a, b)

    def test_case_insensitive(self):
        self.assertEqual(encode("HELLO")["tokens"], encode("hello")["tokens"])


class TestNumbers(unittest.TestCase):
    def test_german_spellings(self):
        cases = {0: "null", 1: "eins", 2: "zwei", 7: "sieben", 10: "zehn",
                 11: "elf", 12: "zwölf", 16: "sechzehn", 21: "einundzwanzig",
                 100: "einhundert", 101: "einhunderteins",
                 365: "dreihundertfünfundsechzig", 1000: "eintausend",
                 21: "einundzwanzig", 1000000: "eine Million"}
        for n, w in cases.items():
            self.assertEqual(N.spell_int(n), w, n)

    def test_numbers_become_words(self):
        r = encode("add 2 and 3")
        self.assertIn("numerals->german", r["extensions"])
        self.assertEqual(decode(r["tokens"])["text"], "add zwei and drei")

    def test_negative(self):
        self.assertEqual(N.spell_int(-5), "minus fünf")


class TestModes(unittest.TestCase):
    def test_strict_rejects_digits(self):
        with self.assertRaises(CopialeError):
            encode("value 42", mode="strict")

    def test_strict_rejects_extension_punct(self):
        with self.assertRaises(CopialeError):
            encode("ready?", mode="strict")

    def test_experimental_allows_extension_punct(self):
        r = encode("ready?")
        self.assertIn("?", r["tokens"])

    def test_unsupported_never_silent(self):
        with self.assertRaises(CopialeError):
            encode("cafe \u2603")   # snowman


class TestDecodeBehaviour(unittest.TestCase):
    def test_unknown_token_strict_raises(self):
        with self.assertRaises(CopialeError):
            decode(["zzz", "notatoken"], mode="strict")

    def test_unknown_token_experimental_flags(self):
        r = decode(["zzz", "notatoken"], mode="experimental")
        self.assertIn("notatoken", r["unknown"])

    def test_ambiguity_reported(self):
        r = decode(["grc", "gam", "uu"])
        toks = [t for t, _ in r["ambiguous"]]
        self.assertEqual(set(toks), {"grc", "gam", "uu"})

    def test_colon_repeat(self):
        # lam : -> tt
        self.assertEqual(decode(["lam", ":"])["text"], "tt")
        # colon with no preceding consonant -> note, no crash
        r = decode([":", "lam"])
        self.assertTrue(any("repeat" in n for n in r["notes"]))

    def test_historical_published_line(self):
        # Knight/Megyesi/Schaefer (2011) Appendix A: this token stream is the
        # published transcription of the first ritual line.
        toks = ("pi oh j v hd tri arr eh three c. ah ni arr lam uh b lip uu r o.. zs"
                .split())
        out = decode(toks)["text"]
        self.assertIn("der hocherleuchte", out)

    def test_master_alphabet_line(self):
        # "Die Algebra" (Staatsarchiv Wolfenbüttel) spells the alphabet ordering.
        toks = "b mal n m. b pipe k inf n s. m".split()
        self.assertEqual(decode(toks)["text"].strip(), "v w x y z")


class TestPunctuation(unittest.TestCase):
    def test_period_is_historical(self):
        r = encode("stop.")
        self.assertIn(".", r["tokens"])
        self.assertEqual(decode(r["tokens"])["text"], "stop.")

    def test_extensions_documented(self):
        for ch in ",?;=":
            self.assertIn(ch, K.EXTENDED_PUNCT)


if __name__ == "__main__":
    unittest.main(verbosity=2)
