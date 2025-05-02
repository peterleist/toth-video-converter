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
    curl \
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

# Alapértelmezett parancs - ez megkönnyíti az interaktív használatot
CMD ["bash"]