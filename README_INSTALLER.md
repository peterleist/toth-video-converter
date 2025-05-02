# Videó MPG Konvertáló - Windows telepítő készítése

Ez a dokumentum leírja, hogyan készíthet Windows telepítőt a Videó MPG Konvertáló alkalmazáshoz.

## Előfeltételek

1. **Python 3.6+** telepítése Windows rendszeren
2. **Inno Setup** telepítése - [Letöltési link](https://jrsoftware.org/isdl.php)
3. Internet kapcsolat az FFmpeg letöltéséhez

## Telepítő készítésének lépései

### 1. Szükséges Python csomagok telepítése

```shell
pip install pyinstaller
```

### 2. Alkalmazás ikon létrehozása (opcionális)

Készítsen egy `app_icon.ico` fájlt az alkalmazáshoz (32x32, 48x48, 64x64 és 256x256 méretű ikonokkal).

### 3. Az EXE fájl és a szükséges fájlok létrehozása

Futtassa a `build_exe.py` szkriptet:

```shell
python build_exe.py
```

Ez a szkript a következőket végzi el:
- PyInstaller telepítése (ha még nem lenne telepítve)
- Az alkalmazás lefordítása EXE fájllá
- FFmpeg letöltése és előkészítése a telepítőhöz

### 4. A telepítő létrehozása

1. Nyissa meg az Inno Setup Compiler programot
2. Nyissa meg az `installer.iss` fájlt
3. Válassza a "Build" -> "Compile" opciót

A telepítő az `installer` mappában jön létre `VideoConverterSetup.exe` néven.

## Telepítő futtatása

A `VideoConverterSetup.exe` fájlt futtassa a célszámítógépen. A telepítő:

1. Telepíti az alkalmazást a Program Files mappába (alapértelmezésként)
2. Telepíti az FFmpeg-et
3. Beállítja a környezeti változókat
4. Létrehoz parancsikonokat a Start menüben és (opcionálisan) az asztalon

## Megjegyzések

- A telepítő adminisztrátori jogosultságokat igényel a Program Files mappába történő telepítéshez és a környezeti változók beállításához.
- Ha problémát tapasztal az FFmpeg-el (pl. "FFmpeg hiányzik" hiba), ellenőrizze, hogy a telepítés során hozzáadta-e az FFmpeg mappát a PATH környezeti változóhoz, vagy indítsa újra a számítógépet a telepítés után.