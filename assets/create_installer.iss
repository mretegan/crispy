[Setup]
AppId={{1B71F614-D6B1-4E28-83C8-E04068C7F91A}
AppName=Crispy
AppVersion=0.6.0
AppVerName=Crispy
AppPublisher=Marius Retegan
AppPublisherURL=https://github.com/mretegan/crispy
AppSupportURL=https://github.com/mretegan/crispy
AppUpdatesURL=https://github.com/mretegan/crispy/releases
DefaultDirName={pf}\Crispy
DefaultGroupName=Crispy
LicenseFile=..\LICENSE.txt
OutputDir=..\..\artifacts
OutputBaseFilename=Crispy-0.6.0-x64
Compression=lzma
SolidCompression=yes
; Remove for 32-bit applications
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "..\..\build\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs
Source: "crispy.ico"; DestDir: "{app}"

[Icons]
; Don't forget to copy crispy.ico to the build folder.
Name: "{group}\Crispy"; Filename: "{app}\crispy.exe"; IconFilename: "{app}\crispy.ico"
Name: "{group}\Uninstall"; Filename: "{uninstallexe}"
