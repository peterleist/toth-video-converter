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