#define AppName "SleepSwitcher"
#define AppVersion "1.1.0"
#define AppPublisher "sway11466"
#define AppURL "https://github.com/sway11466/SleepSwitcher"
#define AppExeName "SleepSwitcher.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
OutputDir=..\dist
OutputBaseFilename=SleepSwitcher_Setup
SetupIconFile=..\assets\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"

[Tasks]
Name: "startup"; Description: "Windows 起動時に自動的に開始する"; GroupDescription: "追加タスク:"

[Files]
Source: "..\dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\assets\readme.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\assets\syukujitsu.csv"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\アンインストール"; Filename: "{uninstallexe}"
Name: "{userstartup}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: startup

[Run]
Filename: "{app}\{#AppExeName}"; Description: "インストール完了後に {#AppName} を起動する"; Flags: nowait postinstall skipifsilent
