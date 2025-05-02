#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
import locale

# Karakterkódolás beállítása
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

def check_dependencies():
    """Ellenőrzi és telepíti a szükséges függőségeket"""
    dependencies = ["pyinstaller", "pillow"]
    
    for dep in dependencies:
        try:
            subprocess.run(
                ["pip", "show", dep],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            print(f"{dep} már telepítve van.")
        except subprocess.CalledProcessError:
            print(f"{dep} nincs telepítve. Telepítés...")
            try:
                subprocess.run(
                    ["pip", "install", dep],
                    check=True
                )
                print(f"{dep} sikeresen telepítve.")
            except subprocess.CalledProcessError as e:
                print(f"Hiba a {dep} telepítése során: {e}")
                return False
    
    return True

def validate_icon():
    """Ellenőrzi és érvényes ikonná konvertálja az ikont"""
    icon_path = Path("app_icon.ico")
    svg_path = Path("video-conversion-svgrepo-com.svg")
    
    if not icon_path.exists() or os.path.getsize(icon_path) < 100:  # Ha nem létezik vagy túl kicsi
        print("Érvényes ikon nem található. Kísérlet új ikon létrehozására...")
        
        try:
            # Ha van SVG, akkor megpróbáljuk konvertálni
            if svg_path.exists():
                # Pillow és cairosvg használatával konvertálunk
                try:
                    import cairosvg
                    from PIL import Image
                    import io
                    
                    # Először PNG-vé konvertáljuk
                    png_data = cairosvg.svg2png(url=str(svg_path))
                    png_image = Image.open(io.BytesIO(png_data))
                    
                    # Különböző méretek hozzáadása az .ico fájlhoz
                    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128)]
                    images = []
                    for size in sizes:
                        img_copy = png_image.copy()
                        img_copy.thumbnail(size, Image.LANCZOS)
                        images.append(img_copy)
                    
                    # ICO fájl mentése
                    images[0].save(
                        icon_path, 
                        format="ICO", 
                        sizes=[(img.width, img.height) for img in images],
                        append_images=images[1:]
                    )
                    print("Icon sikeresen létrehozva az SVG fájlból.")
                except ImportError:
                    print("cairosvg nincs telepítve, telepítés...")
                    subprocess.run(["pip", "install", "cairosvg"], check=True)
                    print("Kérjük, futtassa újra a szkriptet.")
                    return False
            else:
                # Ha nincs SVG, egyszerű színes ikont készítünk
                from PIL import Image, ImageDraw
                
                # 256x256-os alapkép
                img = Image.new('RGBA', (256, 256), color=(73, 109, 137, 255))
                d = ImageDraw.Draw(img)
                
                # Egyszerű alakzat rajzolása
                d.ellipse((50, 50, 206, 206), fill=(255, 255, 255, 180))
                d.rectangle((90, 90, 166, 166), fill=(255, 128, 0, 200))
                
                # Több méretben mentjük
                sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
                images = []
                
                for size in sizes:
                    img_copy = img.copy()
                    img_copy.thumbnail(size, Image.LANCZOS)
                    images.append(img_copy)
                
                # ICO fájlba mentés
                images[0].save(
                    icon_path, 
                    format="ICO", 
                    sizes=[(img.width, img.height) for img in images],
                    append_images=images[1:]
                )
                print("Alapértelmezett ikon létrehozva.")
        
        except Exception as e:
            print(f"Hiba az ikon létrehozása során: {e}")
            print("Az alkalmazás ikon nélkül lesz felépítve.")
            return False
            
    return True

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
    
    # Ikon paraméter csak akkor, ha az ikon létezik
    icon_path = Path("app_icon.ico")
    icon_param = ["--icon=app_icon.ico"] if icon_path.exists() and os.path.getsize(icon_path) > 100 else []
    
    # PyInstaller parancs futtatása
    pyinstaller_cmd = [
        "pyinstaller",
        "--name=VideoConverter",
        "--windowed",
        "--onefile",
    ] + icon_param + [
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
    print("FFmpeg letoltese...")  # Ékezetek nélkül a biztonság kedvéért
    ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    
    try:
        # Letöltési könyvtár létrehozása
        os.makedirs("temp", exist_ok=True)
        
        # FFmpeg letöltése
        print("FFmpeg letoltese folyamatban...")
        download_cmd = ["curl", "-L", ffmpeg_url, "-o", "temp/ffmpeg.zip"]
        subprocess.run(download_cmd, check=True, encoding='utf-8')
        
        # Kicsomagolás
        print("FFmpeg kicsomagolasa...")
        try:
            # PowerShell helyett alternatív módszer, ha elérhető
            try:
                import zipfile
                with zipfile.ZipFile("temp/ffmpeg.zip", 'r') as zip_ref:
                    zip_ref.extractall("temp/ffmpeg")
                print("Kicsomagolas sikeres (Python zipfile modullal).")
            except Exception as zip_err:
                print(f"Python kicsomagolas sikertelen, PowerShell hasznalata: {zip_err}")
                # Ha a Python kicsomagolás nem működik, próbáljuk PowerShell-lel ASCII karakterekkel
                expand_cmd = ["powershell", "Expand-Archive", "-Path", "temp/ffmpeg.zip", 
                            "-DestinationPath", "temp/ffmpeg", "-Force"]
                subprocess.run(expand_cmd, check=True, encoding='ascii', errors='replace')
        except Exception as unzip_err:
            print(f"Kicsomagolas hiba: {unzip_err}")
            raise
        
        # FFmpeg bin könyvtár másolása a dist könyvtárba
        print("FFmpeg binarisok masolasa...")
        
        # Könyvtárstruktúra ellenőrzése
        temp_ffmpeg = Path("temp/ffmpeg")
        
        # Megpróbáljuk megtalálni a bin könyvtárat
        bin_dirs = list(temp_ffmpeg.glob("*/bin"))
        
        if not bin_dirs:
            print("A bin konyvtar nem talalhato. Konyvtarstruktura ellenorzese:")
            for item in temp_ffmpeg.glob("*"):
                print(f"  - {item.relative_to(temp_ffmpeg)}")
                
            # Keressünk .exe fájlokat bárhol
            exe_files = list(temp_ffmpeg.glob("**/*.exe"))
            if exe_files:
                print(f"{len(exe_files)} .exe fajl talalhato. Az elso 3:")
                for exe in exe_files[:3]:
                    print(f"  - {exe.relative_to(temp_ffmpeg)}")
                    
                # Ha találtunk .exe fájlokat, használjuk őket
                print("FFmpeg binarisok masolasa a talalt .exe fajlokbol...")
                ffmpeg_dir = Path("dist/ffmpeg")
                os.makedirs(ffmpeg_dir, exist_ok=True)
                
                for exe in exe_files:
                    if exe.name.lower() in ['ffmpeg.exe', 'ffprobe.exe', 'ffplay.exe']:
                        print(f"  - {exe.name} masolasa")
                        shutil.copy(exe, ffmpeg_dir)
                        
                print("FFmpeg binarisok masolasa kesz.")
                return True
            else:
                raise Exception("Nem talalhato FFmpeg binaris a letoltott archivumban")
            
        # Ha megtaláltuk a bin könyvtárat
        ffmpeg_bin = bin_dirs[0]
        print(f"FFmpeg bin konyvtar: {ffmpeg_bin}")
        
        os.makedirs("dist/ffmpeg", exist_ok=True)
        
        # FFmpeg binárisok másolása
        copied = 0
        for file in ffmpeg_bin.glob("*.exe"):
            dest = Path("dist/ffmpeg") / file.name
            print(f"  - {file.name} masolasa")
            shutil.copy(file, dest)
            copied += 1
            
        if copied == 0:
            raise Exception("Nem talalhato .exe fajl az FFmpeg bin konyvtarban")
            
        print(f"FFmpeg sikeresen letoltve es elokeszitve. ({copied} fajl masolva)")
        return True
    except Exception as e:
        print(f"Hiba az FFmpeg letoltese soran: {str(e).encode('ascii', 'replace').decode('ascii')}")
        return False

def main():
    if not check_dependencies():
        sys.exit(1)
    
    if not validate_icon():
        print("Figyelmeztetés: Az ikon validálása sikertelen, de folytatjuk az exe építését.")
        
    if not build_exe():
        sys.exit(1)
    
    if not download_ffmpeg():
        sys.exit(1)
    
    print("Minden előkészítés sikeresen befejeződött!")
    print("Most futtassa az Inno Setup szkriptet a telepítő létrehozásához.")

if __name__ == "__main__":
    main()