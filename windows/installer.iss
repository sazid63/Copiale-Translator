; Copiale Translator — Windows installer script (Inno Setup 6).
; Build the app first (from the repo root):
;   python -m PyInstaller --noconfirm --onefile --windowed ^
;     --name CopialeTranslator --icon windows/icon.ico --paths . ^
;     --distpath windows/dist --workpath windows/build ^
;     windows/copiale_gui.py
; Then compile this script:
;   iscc windows/installer.iss
; Output: windows/Output/CopialeTranslator-Setup-1.0.0.exe
; No admin rights needed (per-user install).

#define MyAppName "Copiale Translator"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "sazid63"
#define MyAppExeName "CopialeTranslator.exe"

[Setup]
AppId={{805CF89B-5F98-449C-AB3A-443ABB2F4EE7}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\Copiale Translator
PrivilegesRequired=lowest
OutputDir=Output
OutputBaseFilename=CopialeTranslator-Setup-1.0.0
SetupIconFile=icon.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
UninstallDisplayName=Copiale Translator

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\CopialeTranslator.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Copiale Translator"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\Copiale Translator"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,Copiale Translator}"; Flags: nowait postinstall skipifsilent
