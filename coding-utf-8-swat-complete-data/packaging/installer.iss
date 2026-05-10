; Inno Setup installer for SWAT Weather App
; Build prerequisites:
;   1) Build the app bundle via PyInstaller (dist\SWAT_Weather_App\)
;   2) Install Inno Setup (ISCC.exe available)
;
; Build:
;   iscc packaging\installer.iss

#define AppName "SWAT Weather App"
#define AppExeName "SWAT_Weather_App.exe"
#define AppPublisher "Shujat Mehdi"
#define AppVersion "1.0.0"

[Setup]
AppId={{8B36E9D4-6B10-4C1A-8B0C-9A3B1A2C3D4E}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
OutputDir=dist_installer
OutputBaseFilename=SWAT_Weather_App_Setup
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
WizardStyle=modern

[Tasks]
Name: "desktopicon"; Description: "Create a Desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked
Name: "startup"; Description: "Run {#AppName} at Windows startup"; GroupDescription: "Startup:"; Flags: unchecked

[Files]
; Copy the entire PyInstaller onedir bundle
Source: "..\dist\SWAT_Weather_App\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{commondesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Registry]
; Optional startup entry
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#AppName}"; ValueData: """{app}\{#AppExeName}"""; Tasks: startup; Flags: uninsdeletevalue

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent
