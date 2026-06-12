[Setup]
AppId={{B8F7E3A2-4D5C-4E8F-9A1B-2C3D4E5F6A7B}}
AppName=DucK-Downloader-GUI
AppVersion=1.0.3
AppPublisher=Xiaomi MiMo
DefaultDirName={autopf}\DucK-Downloader-GUI
DefaultGroupName=DucK-Downloader-GUI
OutputDir=C:\Qyyy\TikTokDownloader-master\installer
OutputBaseFilename=DucK-Downloader-GUI-1.0.3-Setup
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
Source: "C:\Qyyy\TikTokDownloader-master\dist\DucK-Downloader-GUI\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\DucK-Downloader-GUI"; Filename: "{app}\DucK-Downloader-GUI.exe"
Name: "{group}\{cm:UninstallProgram,DucK-Downloader-GUI}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\DucK-Downloader-GUI"; Filename: "{app}\DucK-Downloader-GUI.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\DucK-Downloader-GUI.exe"; Description: "{cm:LaunchProgram,DucK-Downloader-GUI}"; Flags: nowait postinstall skipifsilent
