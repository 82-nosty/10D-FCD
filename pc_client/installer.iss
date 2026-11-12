; 10D FCD - Professional Commercial Inno Setup Installer Script
; Packages dist/10D_FCD directory into 10D_FCD_Setup_v2.1.8.exe

#define MyAppName "10D FCD"
#define MyAppVersion "2.1.8"
#define MyAppPublisher "Nosty"
#define MyAppURL "https://github.com/82-nosty/10D-FCD"
#define MyAppExeName "10D_FCD.exe"

[Setup]
AppId={{9F82A028-10DF-4FCD-A882-E7A492C10DFB}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\10D_FCD
DisableProgramGroupPage=yes
OutputBaseFilename=10D_FCD_Setup_v{#MyAppVersion}
OutputDir=Output
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
SetupIconFile=assets\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "dist\10D_FCD\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

