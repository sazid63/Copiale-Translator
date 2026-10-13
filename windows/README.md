# Copiale Translator — Windows app

## Install it (final version, no Python needed)

1. Open
   [Releases](https://github.com/sazid63/Copiale-Translator/releases)
   and download `CopialeTranslator-Setup-1.0.0.exe`.
2. Double-click the downloaded file.
3. Click **Next → Install** (no admin rights needed).
4. If Windows SmartScreen warns (the installer isn't commercially
   signed), click **"More info" → "Run anyway"**.
5. Open **Start Menu → Copiale Translator**.

That is the whole installation process — one file, one installer.

## Use it

- **Mode dropdown:** Encode (message → tokens) or Decode (tokens → message).
- **Key field (optional):** leave empty for an open message. Type a
  passphrase, or press **New key** for a fresh shareable one, then
  **Translate**.
- **To send a secret:** share the encoded tokens **AND** the key. The other
  person pastes both into Decode with the same key. Without the key it
  reads as gibberish.
- **Strict mode** checkbox: historical symbols only (keys rejected, same
  rule as everywhere else in this project).
- **Swap** flips the direction; **Clear** empties the fields.

## Uninstall it

Settings → Apps → Copiale Translator → Uninstall. Removes everything.

## For developers (rebuild from source)

The installer packages `copiale_gui.py` (same engine as the CLI and the
Android app — one `Copiale-Lock-v2` key derivation everywhere):

```powershell
# 1. build a single-file exe (needs: pip install pyinstaller)
python -m PyInstaller --noconfirm --onefile --windowed `
  --name CopialeTranslator --icon windows/icon.ico --paths . `
  --distpath windows/dist --workpath windows/build `
  windows/copiale_gui.py

# 2. compile the installer (needs Inno Setup 6)
iscc windows/installer.iss
# → windows/Output/CopialeTranslator-Setup-1.0.0.exe
```

Build outputs (`dist/`, `build/`, `Output/`) are gitignored; finished
installers ship via GitHub Releases, never in git.
