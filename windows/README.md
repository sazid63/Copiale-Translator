# Copiale Translator — Windows app

## Which file do I click?

**Easiest (no Python needed):** download
`CopialeTranslator-Setup-1.0.0.exe` from
[Releases](https://github.com/sazid63/Copiale-Translator/releases),
double-click it, and follow the installer (no admin rights needed). It adds
a Start Menu entry and an uninstaller. If Windows SmartScreen warns (the
installer isn't commercially signed), click "More info" → "Run anyway".

**From source (needs Python 3.9+):** open this `windows` folder and
double-click **`Copiale_Translator.bat`** — the translator window opens.

If you downloaded this project as a ZIP from GitHub: unzip it first.

To remove the installed app: Settings → Apps → Copiale Translator →
Uninstall (or run `unins000.exe` in its install folder).

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
