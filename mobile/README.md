# Copiale Translator — Android app

Flutter port of the Copiale cipher translator (`../copiale/`), with the
optional shared-key locked mode. Works **fully offline** — no permissions,
no network, no accounts.

## Project layout

```text
mobile/
  pubspec.yaml            app metadata + deps (crypto, share_plus)
  lib/
    main.dart             app shell, night-signals theme, bottom nav
    copiale/
      key_data.dart       symbol key (port of copiale/key.py)
      numbers.dart        German number spelling (port of numbers.py)
      cipher.dart         encode/decode (port of translate.py)
      locked.dart         shared-key layer (port of locked.py, v2)
      errors.dart         CopialeError
    ui/
      cipher_screen.dart  encode/decode workspace + key row + send
      symbols_screen.dart browsable symbol inventory
      about_screen.dart   history vs extensions, honest limits
      theme.dart          palette
  test/
    cipher_test.dart      vector + rule tests (MUST pass before release)
    test_vectors.json     cross-language vectors from Python (see tool/)
  tool/
    make_vectors.py       regenerates test_vectors.json from Python
    make_icons.py         regenerates launcher icons (stdlib only)
  android/                Play-ready config (see below)
```

## Key interoperability (important)

The app and the Python translator share one fully specified derivation,
"Copiale-Lock-v2" (SHA-256 counter stream → Fisher-Yates shuffle — see
`../spec` notes in the research repo and `locked.dart`). A key created in
the app unlocks in Python and vice versa. This is enforced by
`test/test_vectors.json`, generated from the Python reference:

```powershell
# regenerate vectors after any cipher change (from the research repo root)
python mobile/tool/make_vectors.py <research-root> mobile/test/test_vectors.json
```

If `flutter test` fails on vectors, the cipher port has drifted — do NOT
release until it passes. Without matching derivation the key is useless.

## Build & test (on a machine with Flutter installed)

```powershell
cd mobile
flutter pub get
flutter analyze
flutter test            # must be all green, vectors included
flutter build apk --release                 # sideloadable APK
flutter build appbundle --release           # Play Store upload (.aab)
```

Requires Flutter 3.x (Dart >=3.0), Java 17, Android SDK with API 35.
First Gradle build downloads its distribution automatically via the
committed wrapper (`android/gradle/wrapper/`).

## Play Store release checklist

1. `flutter test` green (vectors included).
2. Bump `version:` in `pubspec.yaml` (e.g. `1.0.1+2`).
3. Release signing (one-time, ON YOUR MACHINE ONLY):
   ```powershell
   keytool -genkey -v -keystore copiale-release.jks -alias copiale `
     -keyalg RSA -keysize 2048 -validity 10000
   ```
   Create `android/key.properties` (NEVER committed — gitignored):
   ```properties
   storePassword=...
   keyPassword=...
   keyAlias=copiale
   storeFile=C:/path/to/copiale-release.jks
   ```
   Then point the `release` build type at it (see `android/app/build.gradle`;
   it currently signs release with debug keys so test builds work).
   **Back up the keystore + passwords offline. Losing them means a new
   Play listing — Google cannot recover them.**
4. `flutter build appbundle --release` → upload
   `build/app/outputs/bundle/release/app-release.aab` in Play Console.
5. Listing needs: app icon (in-repo), 2+ screenshots, feature graphic,
   short/full description, privacy policy ("works offline, collects no
   data"), content rating questionnaire, target audience + news declarations.
6. Play's target-API rule: keep `targetSdk` current (template delegates to
   `flutter.targetSdkVersion`; update Flutter if Play asks for newer).

## Port-fidelity notes (vs Python)

Deliberately identical behaviour, including quirks: ß→ss normalisation,
`:` doubling, logogram markers, strict-mode rejections, homophone
round-robin, German number words (lossy), error message texts. Known
tolerated divergences: `\d` is ASCII-only in Dart (Python matches Unicode
digits); exotic Unicode whitespace classification may differ; huge integers
(>= 2^63 digits) are rejected with the same "number too large" message.
