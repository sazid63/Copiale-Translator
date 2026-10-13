# Copiale Cipher Translator

A small, dependency-free Python toolkit for the historical Copiale cipher
(Knight, Megyesi & Schaefer, 2011/2012). It encodes plaintext into cipher
tokens and decodes cipher tokens back into text, keeping historically
supported behavior clearly separate from modern extensions.

Standard library only. Python 3.9+.

## Quick start

```powershell
# plaintext -> cipher tokens
python -m copiale.cli encode "the secret master"

# cipher tokens -> plaintext
python -m copiale.cli decode "tri gam"

# encode then decode (show the round-trip)
python -m copiale.cli roundtrip "hello world"

# list the symbol inventory
python -m copiale.cli symbols

# run built-in checks
python -m copiale.cli selftest
python -m unittest discover -s tests
```

## Layout

```text
copiale/            the translator package
  key.py            symbol inventory (historical / convention / extension)
  numbers.py        German number spelling (extension)
  translate.py      encode() / decode()
  cli.py            command-line interface
tests/
  test_translator.py  round-trip, mode, and rule-specific tests
```

## Modes

* **strict** — only historically documented features. Numerals and modern
  punctuation tokens are rejected (nothing is altered silently).
* **experimental** (default) — additionally enables the approved extensions
  (numerals spelled as German words, and the punctuation tokens `, ? ! ; =`).
  Every extension use is reported.

Unsupported input always raises an error; it is never dropped quietly.

---

## Locked (keyed) mode — optional (modern extension, never historical)

No key needed for normal use. When two people need privacy, the sender locks
the message with a passphrase:

```powershell
# 1. make a key (or pick your own passphrase)
python -m copiale.cli keygen

# 2. lock a message (share the printed tokens AND the key)
python -m copiale.cli encode "meet at midnight" --key "my-secret-key"

# 3. recipient unlocks with the same key
python -m copiale.cli decode "<tokens>" --key "my-secret-key"
```

Or in one step (the encoder gives you a fresh key to share):

```powershell
python -m copiale.cli encode "meet at midnight" --new-key
```

Without the key (or with the wrong key) the same tokens decode to
substituted gibberish, not the message. Keys are case-sensitive, rejected in
`--strict` mode, and are a casual-privacy convenience — not audited
cryptography. `ß` normalises to `ss`, as in unlocked mode.
Locked derivation: `Copiale-Lock-v2` (portable across the Python translator
and the mobile app, so keys interoperate).

## Examples

```powershell
python -m copiale.cli encode "ok"
# tri gam

python -m copiale.cli decode "tri gam"
# ok

python -m copiale.cli decode "bas :"
# cc   (":" repeats the previous consonant)

python -m copiale.cli encode "hi," --strict
# ERROR: unsupported input characters (nothing was silently altered): ','
```

## Honest limitations

* The translation is a substitution over letters.
* Numerals are lossy: `2` -> `zwei` -> decodes to `zwei`, not `2`.
* `ß` normalises to `ss` (period spelling).
* A few symbols are inherently ambiguous (`grc` = S/SS, `gam` = H/K,
  `uu` = EN/EM); the translator resolves them by documented convention and
  reports when it does.
* Capitalisation is not preserved (the cipher has none).
* English is a mechanical extension, not a documented historical use.

## Sources

* Knight, Megyesi & Schaefer, "The Copiale Cipher" (ACL 2011 workshop) and
  "Secrets of the Copiale Cipher" (2012).
