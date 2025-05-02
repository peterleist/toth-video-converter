#!/usr/bin/env python3
"""
Build Script

Ez a szkript a PyInstaller segítségével egy futtatható .exe fájlt készít
a videó konvertáló alkalmazásból Windows platformra.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """Ellenőrzi, hogy a PyInstaller telepítve van-e"""
    try:
        subprocess.run(
            ["pip", "show", "pyinstaller"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return True
    except subprocess.CalledProcessError:
        print("PyInstaller nincs telepítve. Telepítés...")
        try:
            subprocess.run(
                ["pip", "install", "pyinstaller"],
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Hiba a PyInstaller telepítése során: {e}")
            return False

def build_exe():
    """Létrehozza az exe fájlt a PyInstaller segítségével"""
    print("Alkalmazás fordítása exe fájllá...")
    
    # Tisztítás
    dist_dir = Path("dist")
    build_dir = Path("build")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # PyInstaller parancs futtatása
    pyinstaller_cmd = [
        "pyinstaller",
        "--name=VideoConverter",
        "--windowed",
        "--onefile",
        "--icon=app_icon.ico",  # Ikonfájl (ezt létre kell hozni)
        "convert_gui.py"
    ]
    
    try:
        subprocess.run(pyinstaller_cmd, check=True)
        print("Az exe fájl sikeresen elkészült: dist/VideoConverter.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Hiba az exe fájl létrehozása során: {e}")
        return False

def download_ffmpeg():
    """Letölti és kibontja az FFmpeg-et"""
    print("FFmpeg letöltése...")
    ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    
    try:
        # Letöltési könyvtár létrehozása
        os.makedirs("temp", exist_ok=True)
        
        # FFmpeg letöltése
        subprocess.run(
            ["curl", "-L", ffmpeg_url, "-o", "temp/ffmpeg.zip"],
            check=True
        )
        
        # Kicsomagolás
        subprocess.run(
            ["powershell", "Expand-Archive", "-Path", "temp/ffmpeg.zip", "-DestinationPath", "temp/ffmpeg", "-Force"],
            check=True
        )
        
        # FFmpeg bin könyvtár másolása a dist könyvtárba
        ffmpeg_bin = next(Path("temp/ffmpeg").glob("*/bin"))
        os.makedirs("dist/ffmpeg", exist_ok=True)
        
        # FFmpeg binárisok másolása
        for file in ffmpeg_bin.glob("*.exe"):
            shutil.copy(file, "dist/ffmpeg")
            
        print("FFmpeg sikeresen letöltve és előkészítve.")
        return True
    except Exception as e:
        print(f"Hiba az FFmpeg letöltése során: {e}")
        return False

def main():
    if not check_pyinstaller():
        sys.exit(1)
        
    if not build_exe():
        sys.exit(1)
    
    if not download_ffmpeg():
        sys.exit(1)
    
    print("Minden előkészítés sikeresen befejeződött!")
    print("Most futtassa az Inno Setup szkriptet a telepítő létrehozásához.")

if __name__ == "__main__":
    main()