[Setup]
; Alapvető alkalmazásinformációk
AppName=Videó MPG Konvertáló
AppVersion=1.0
AppPublisher=Felhasználó
AppPublisherURL=https://www.example.com
AppSupportURL=https://www.example.com
AppUpdatesURL=https://www.example.com

; Telepítő beállítások
DefaultDirName={autopf}\Video MPG Converter
DefaultGroupName=Videó MPG Konvertáló
DisableProgramGroupPage=yes
OutputDir=installer
OutputBaseFilename=VideoConverterSetup
Compression=lzma
SolidCompression=yes
;SetupIconFile=app_icon.ico
WizardStyle=modern

; Admin jogosultságok kérése - szükséges a Program Files mappába telepítéshez
PrivilegesRequired=admin

[Languages]
Name: "hungarian"; MessagesFile: "compiler:Languages\Hungarian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Az exe fájl és minden egyéb fájl a dist mappából
Source: "dist\VideoConverter.exe"; DestDir: "{app}"; Flags: ignoreversion
; FFmpeg fájlok
Source: "dist\ffmpeg\*"; DestDir: "{app}\ffmpeg"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start menü és asztali parancsikonok
Name: "{group}\Videó MPG Konvertáló"; Filename: "{app}\VideoConverter.exe"
Name: "{autodesktop}\Videó MPG Konvertáló"; Filename: "{app}\VideoConverter.exe"; Tasks: desktopicon

[Run]
; Opció a telepítés befejezése után az alkalmazás indítására
Filename: "{app}\VideoConverter.exe"; Description: "{cm:LaunchProgram,Videó MPG Konvertáló}"; Flags: nowait postinstall skipifsilent

[Code]
// Környezeti változók kezelése
procedure CurStepChanged(CurStep: TSetupStep);
var
  Path, NewPath: string;
begin
  if CurStep = ssPostInstall then
  begin
    // FFmpeg hozzáadása a PATH környezeti változóhoz
    if RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', Path) then
    begin
      NewPath := Path;
      if Pos(ExpandConstant('{app}\ffmpeg'), NewPath) = 0 then
      begin
        if Copy(NewPath, Length(NewPath), 1) <> ';' then
          NewPath := NewPath + ';';
        NewPath := NewPath + ExpandConstant('{app}\ffmpeg') + ';';
        RegWriteStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', NewPath);
      end;
    end;
  end;
end;

// Telepítés előtti ellenőrzés
function InitializeSetup(): Boolean;
var
  PrevPath: string;
  InstallPath: string;
begin
  Result := True;
  
  // Ellenőrizzük, hogy van-e korábbi telepítés
  if RegQueryStringValue(HKEY_LOCAL_MACHINE,
    'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}_is1',
    'InstallLocation', PrevPath) then
  begin
    // Ha találtunk korábbi telepítést, kérdezzük meg a felhasználót
    if MsgBox('Egy korábbi telepítés már létezik. Szeretné eltávolítani a régi verziót a folytatás előtt?',
       mbConfirmation, MB_YESNO) = IDYES then
    begin
      // Lekérjük a korábbi uninstallstring-et
      if RegQueryStringValue(HKEY_LOCAL_MACHINE,
        'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}_is1',
        'UninstallString', InstallPath) then
      begin
        // Lefuttatjuk az uninstallert
        Exec(RemoveQuotes(InstallPath), '/SILENT', '', SW_SHOW, ewWaitUntilTerminated, Result);
      end;
    end;
  end;
end;