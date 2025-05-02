# Windows telepítő készítése macOS rendszeren

Ez az útmutató segít Windows telepítő létrehozásában macOS környezetben a Videó MPG Konvertáló alkalmazáshoz.

## 1. módszer: Virtuális gép használata

Ez a legmegbízhatóbb módszer, ahol egy Windows virtuális környezetben készítjük el a telepítőt.

### Előfeltételek

1. **VirtualBox** vagy **Parallels** telepítése macOS rendszeren
2. **Windows 10/11** telepítőlemez képfájl (.iso)
3. Legalább 50 GB szabad hely és 4 GB RAM a virtuális gép futtatásához

### Lépések

1. **Telepítse a virtualizációs szoftvert**
   - [VirtualBox letöltése](https://www.virtualbox.org/wiki/Downloads) (ingyenes)
   - VAGY [Parallels letöltése](https://www.parallels.com/) (fizetős, de felhasználóbarátabb)

2. **Hozzon létre egy Windows virtuális gépet**
   - Kövesse a VirtualBox/Parallels útmutatóját Windows telepítéséhez
   - Javasolt legalább 2 CPU mag, 4 GB RAM és 50 GB tárterület kiosztása

3. **Állítsa be a mappamegosztást**
   - A Virtualbox-ban: Devices > Shared Folders > Shared Folder Settings
   - Parallels-ben: Preferences > Sharing > Add (+) 
   - Ossza meg a `/Users/ispeterl/Documents/Convert` mappát a virtuális géppel

4. **A Windows VM-en belül:**
   - Telepítse a Python-t (3.6 vagy újabb): https://www.python.org/downloads/windows/
   - Telepítse az Inno Setup-ot: https://jrsoftware.org/isdl.php
   - Telepítse a szükséges Python csomagokat: `pip install pyinstaller`
   - Másolja át a projektfájlokat a megosztott mappából
   - Kövesse a README_INSTALLER.md útmutatót a Windows telepítő létrehozásához

## 2. módszer: Docker és Wine használata

Ha nem szeretne virtuális gépet telepíteni, használhatja a Wine-t Docker konténerben is.

### Előfeltételek

1. **Docker Desktop** telepítése macOS-en: https://www.docker.com/products/docker-desktop/

### Lépések

1. **Hozzon létre egy Dockerfile-t**

   Hozzon létre egy új fájlt `Dockerfile` néven a projekt gyökérkönyvtárában:

```dockerfile
FROM ubuntu:latest

# Szükséges csomagok telepítése
RUN apt-get update && apt-get install -y \
    wine64 \
    winetricks \
    wget \
    unzip \
    xvfb \
    python3 \
    python3-pip \
    python3-setuptools \
    && rm -rf /var/lib/apt/lists/*

# Wine környezet beállítása
ENV WINEARCH=win64
ENV WINEPREFIX=/root/.wine
ENV DISPLAY=:0

# Inno Setup telepítése Wine alatt
RUN mkdir -p /innosetup && \
    cd /innosetup && \
    wget -q https://files.jrsoftware.org/is/6/innosetup-6.2.1.exe && \
    xvfb-run wine innosetup-6.2.1.exe /VERYSILENT /SUPPRESSMSGBOXES /NORESTART

# Python telepítése Wine alatt
RUN wget -q https://www.python.org/ftp/python/3.9.7/python-3.9.7-amd64.exe && \
    xvfb-run wine python-3.9.7-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 && \
    rm python-3.9.7-amd64.exe

# PyInstaller telepítése Wine alatt
RUN xvfb-run wine python -m pip install pyinstaller

# Munkakönyvtár beállítása
WORKDIR /app

# Alkalmazás fájlok másolása
COPY . /app/

# Alapértelmezett parancs
CMD ["bash"]
```

2. **Docker image építése**

   Nyisson egy terminált a projekt könyvtárában, és futtassa:

```bash
docker build -t video-converter-builder .
```

3. **A Docker konténer futtatása** 

```bash
docker run -it --rm -v $(pwd):/app video-converter-builder bash
```

4. **A konténeren belül**

```bash
# Az EXE fájl létrehozása
xvfb-run wine python build_exe.py

# A telepítő létrehozása
cd /app
xvfb-run wine /root/.wine/drive_c/Program\ Files\ \(x86\)/Inno\ Setup\ 6/ISCC.exe installer.iss
```

5. **Az elkészült telepítő kimentése** 

A telepítő az `installer` mappában jön létre `VideoConverterSetup.exe` néven, ami közvetlenül elérhető lesz a Mac gépen is, mivel a mappát összekapcsoltuk.

## 3. módszer: GitHub Actions használata

Ha ismeri a GitHub-ot, akkor a GitHub Actions segítségével is létrehozhat Windows telepítőt anélkül, hogy helyi szoftvereket kellene telepítenie.

1. **Hozzon létre egy GitHub repository-t** a projekthez
2. **Töltse fel a fájlokat** a repository-ba
3. **Hozzon létre egy workflow fájlt** `.github/workflows/build-installer.yml` néven:

```yaml
name: Build Windows Installer

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pyinstaller
    
    - name: Download and install Inno Setup
      run: |
        Invoke-WebRequest -Uri "https://jrsoftware.org/download.php/is.exe" -OutFile "is.exe"
        Start-Process -FilePath "is.exe" -ArgumentList "/VERYSILENT /SUPPRESSMSGBOXES /NORESTART" -Wait
    
    - name: Build executable
      run: python build_exe.py
    
    - name: Build installer
      run: |
        & "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
    
    - name: Upload installer
      uses: actions/upload-artifact@v2
      with:
        name: windows-installer
        path: installer/VideoConverterSetup.exe
```

4. **Indítsa el a workflow-t** a GitHub felületen
5. **Töltse le a kész telepítőt** az Artifacts szekcióból a GitHub Actions futtatása után

## Megjegyzések

- A legegyszerűbb megoldás egy Windows VM használata a macOS rendszeren
- A Docker + Wine megoldás bonyolultabb, de nem igényel virtuális gép telepítést
- A GitHub Actions a legegyszerűbb módja a távoli build-elésnek, nincs szükség helyi szoftverekre