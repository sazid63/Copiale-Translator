# Copiale Translator — Windows app

## Which file do I click?

**`Copiale_Translator.bat`** — double-click it and the translator window
opens. That is the only file you ever need to click.

Requirements: Python 3.9+ installed (one time, from python.org — tick
"Add python.exe to PATH" during its setup). No other installs.

If you downloaded this project as a ZIP from GitHub: unzip it first, then
open the `windows` folder and double-click `Copiale_Translator.bat`.

Clickable desktop translator (same engine as the Python CLI and the
Android app). Windows only — standard library Tkinter, no installs
beyond Python 3.9+ itself. No Docker, no Linux, no network.

## Run it

Double-click **`Copiale_Translator.bat`**, or:

```powershell
cd windows
python copiale_gui.py
```

## Use it

- **Mode dropdown:** Encode (message → tokens) or Decode (tokens → message).
- **Key field (optional):** leave empty for an open message. Type a
  passphrase, or press **New key** for a fresh shareable one.
- **Translate**, then copy the result. To send a secret, share the tokens
  **AND** the key — the other person pastes both into Decode with the same
  key. Without the key it reads as gibberish.
- **Strict mode** checkbox: historical symbols only (keys rejected, same
  rule as the CLI).
- **Swap** flips the direction; **Clear** empties the fields.

## Notes

- Keys interoperate with the CLI (`python -m copiale.cli ... --key`)
  and the Android app — one derivation (`Copiale-Lock-v2`) everywhere.
- The key is a casual-privacy convenience, not audited cryptography.
- `ß` normalises to `ss`, as everywhere else in this project.
