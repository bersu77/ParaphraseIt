[Setup]
AppName=ParaphraseIt
AppVersion=1.0
AppPublisher=ParaphraseIt
DefaultDirName={autopf}\ParaphraseIt
DefaultGroupName=ParaphraseIt
UninstallDisplayIcon={app}\ParaphraseIt.exe
OutputDir=installer_output
OutputBaseFilename=ParaphraseIt_Setup
SetupIconFile=assets\icon.ico
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest

[Files]
Source: "dist\ParaphraseIt.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\ParaphraseIt"; Filename: "{app}\ParaphraseIt.exe"; IconFilename: "{app}\icon.ico"
Name: "{group}\Uninstall ParaphraseIt"; Filename: "{uninstallexe}"

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "ParaphraseIt"; ValueData: """{app}\ParaphraseIt.exe"""; Flags: uninsdeletevalue

[Run]
Filename: "{app}\ParaphraseIt.exe"; Description: "Launch ParaphraseIt"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "taskkill"; Parameters: "/F /IM ParaphraseIt.exe"; Flags: runhidden
