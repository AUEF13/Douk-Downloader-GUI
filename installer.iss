[Setup]
AppId={{B8F7E3A2-4D5C-4E8F-9A1B-2C3D4E5F6A7B}}
AppName=DouK-Downloader
AppVersion=1.0.1
AppPublisher=DouK
DefaultDirName={autopf}\DouK-Downloader
DefaultGroupName=DouK-Downloader
OutputDir=C:\Qyyy\TikTokDownloader-master\installer
OutputBaseFilename=DouK-Downloader-1.0.1-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes
PrivilegesRequired=lowest

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "C:\Qyyy\TikTokDownloader-master\dist\DouK-Downloader\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\DouK-Downloader"; Filename: "{app}\DouK-Downloader.exe"
Name: "{group}\{cm:UninstallProgram,DouK-Downloader}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\DouK-Downloader"; Filename: "{app}\DouK-Downloader.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\DouK-Downloader.exe"; Description: "{cm:LaunchProgram,DouK-Downloader}"; Flags: nowait postinstall skipifsilent
