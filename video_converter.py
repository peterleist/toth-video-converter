#!/usr/bin/env python3
'''
Video Converter Script

This script converts video files to MPG format using FFmpeg.
It applies specific parameters to match the could_import.mpg format.
'''

import os
import sys
import subprocess
import argparse
import re
import time
from pathlib import Path
import threading
import traceback


def check_ffmpeg():
    """Check if FFmpeg is installed on the system."""
    try:
        subprocess.run(
            ["ffmpeg", "-version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            check=True
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Error: FFmpeg is not installed or not in your PATH.")
        print("Please install FFmpeg to use this script:")
        print("  macOS: brew install ffmpeg")
        print("  Linux: sudo apt install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        return False


def get_video_duration(file_path):
    """Get the duration of a video file in seconds."""
    try:
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", 
               "-of", "default=noprint_wrappers=1:nokey=1", file_path]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                               text=True, check=True)
        duration = float(result.stdout.strip())
        return duration
    except Exception:
        return None


def convert_to_mpg(input_file, output_file=None, overwrite=False, resolution="720x576", progress_callback=None, quality="medium"):
    """
    Convert a video file to MPG format with specific parameters.
    
    Args:
        input_file: Path to the input video file.
        output_file: Path for the output MPG file. If None, derived from input filename.
        overwrite: Whether to overwrite existing output file.
        resolution: Output video resolution as string, e.g. '720x576'.
        progress_callback: Callback function to report progress (value between 0 and 100)
                          and estimated time remaining in seconds.
        quality: Video quality setting: "low", "medium", "high", "veryhigh", "ultra" or "maximum".
    
    Returns:
        bool: True if conversion was successful, False otherwise.
    """
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        return False
    
    # If output file is not specified, create one based on the input file
    if output_file is None:
        input_path = Path(input_file)
        output_file = str(input_path.with_suffix('.mpg'))
    
    # Check if output file already exists
    if os.path.exists(output_file) and not overwrite:
        print(f"Error: Output file '{output_file}' already exists. Use --overwrite to force conversion.")
        return False
    
    print(f"Converting '{input_file}' to '{output_file}' with resolution {resolution} and quality {quality}...")
    
    # Get video duration for progress calculation
    duration = get_video_duration(input_file)
    
    # Define quality presets with enhanced settings
    quality_presets = {
        "low": {
            "b:v": "2000k",
            "maxrate": "2500k", 
            "bufsize": "3000k",
            "qmin": 4,
            "qmax": 30,
            "trellis": 0,
            "mbd": "simple",
            "filter": None
        },
        "medium": {
            "b:v": "4000k",
            "maxrate": "5000k",
            "bufsize": "6000k",
            "qmin": 3, 
            "qmax": 25,
            "trellis": 1,
            "mbd": "rd",
            "filter": None
        },
        "high": {
            "b:v": "7000k",
            "maxrate": "9000k",
            "bufsize": "12000k",
            "qmin": 2,
            "qmax": 18,
            "trellis": 1,
            "mbd": "rd",
            "filter": "unsharp=5:5:0.5:5:5:0.5"  # Enyhe élesítés
        },
        "veryhigh": {
            "b:v": "10000k", 
            "maxrate": "15000k",
            "bufsize": "18000k",
            "qmin": 1, 
            "qmax": 12,
            "trellis": 2,
            "mbd": "rd",
            "filter": "unsharp=7:7:1.5:7:7:1.5"  # Erősebb élesítés
        },
        "ultra": {
            "b:v": "15000k",
            "maxrate": "20000k",
            "bufsize": "25000k",
            "qmin": 1,
            "qmax": 8,
            "trellis": 2,
            "mbd": "rd",
            "filter": "hqdn3d=4:3:6:4.5,unsharp=9:9:1.8:9:9:1.8"  # Zajszűrés + erős élesítés
        },
        "maximum": {
            "b:v": "25000k",
            "maxrate": "35000k",
            "bufsize": "40000k",
            "qmin": 1,
            "qmax": 5,
            "trellis": 2,
            "mbd": "rd",
            "filter": "hqdn3d=2:1:3:3,unsharp=13:13:2.0:13:13:2.0"  # Finom zajszűrés + maximális élesítés
        }
    }
    
    # Get quality settings (default to medium if invalid quality parameter)
    if quality not in quality_presets:
        quality = "medium"
    
    quality_settings = quality_presets[quality]
    
    # Base FFmpeg command
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", input_file,
        "-c:v", "mpeg2video",        # MPEG-1/2 Video codec
        "-s", resolution,            # Resolution from parameter
        "-r", "25",                  # Frame rate 25 fps
        "-pix_fmt", "yuv420p",       # Planar 4:2:0 YUV
        "-b:v", quality_settings["b:v"],  # Video bitrate based on quality
        "-maxrate", quality_settings["maxrate"],  # Maximum bitrate
        "-bufsize", quality_settings["bufsize"],  # Buffer size
        "-qmin", str(quality_settings["qmin"]),  # Minimum quantizer
        "-qmax", str(quality_settings["qmax"]),  # Maximum quantizer
        "-g", "15",                  # GOP size (keyframe interval)
        "-bf", "2",                  # Maximum 2 B-frames between I and P frames
        "-trellis", str(quality_settings["trellis"]),  # Trellis quantization
        "-mbd", quality_settings["mbd"],  # Macroblock decision algorithm
        "-dc", "10",                 # Intra DC precision
        "-flags", "+ilme+ildct",     # Interlaced motion estimation and DCT
        "-c:a", "mp2",               # MPEG Audio Layer 1/2
        "-ar", "48000",              # Audio sample rate 48000 Hz
        "-b:a", "256k",              # Audio bitrate (increased)
        "-ac", "2",                  # Stereo channels
        "-sample_fmt", "s16",        # 16-bit samples (MP2 codec only supports s16)
        "-f", "mpeg",                # Force MPEG format
        "-progress", "-",            # Output progress information to stdout
    ]
    
    # Add filter if specified
    if quality_settings["filter"]:
        ffmpeg_cmd.extend(["-vf", quality_settings["filter"]])
    
    # Add overwrite option and output file
    ffmpeg_cmd.extend(["-y" if overwrite else "-n", output_file])
    
    try:
        # Start FFmpeg process with pipe for stderr
        process = subprocess.Popen(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )
        
        # Variables to track progress
        start_time = time.time()
        pattern = re.compile(r'time=(\d+):(\d+):(\d+.\d+)')
        last_update_time = 0
        progress_percent = 0
        last_read_time = time.time()
        stall_timeout = 30  # másodperc - ennyi időt várunk válasz nélkül mielőtt beavatkoznánk
        
        # Stderr olvasásra külön szál
        stderr_lines = []
        def read_stderr():
            while True:
                line = process.stderr.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    stderr_lines.append(line)
        
        # Indítsuk el a stderr olvasó szálat
        stderr_thread = threading.Thread(target=read_stderr, daemon=True)
        stderr_thread.start()
        
        # Read output line by line
        while process.poll() is None:
            line = process.stdout.readline()
            
            # Nincs kimenet, de a folyamat még fut
            if not line:
                # Ellenőrizzük, hogy nem állt-e le a feldolgozás (timeout)
                current_time = time.time()
                if current_time - last_read_time > stall_timeout:
                    print(f"FFmpeg process stalled for {stall_timeout} seconds at {progress_percent:.1f}%.")
                    print("Continuing to wait...")
                    # Ne dobja el a folyamatot, várjunk tovább
                
                time.sleep(0.1)  # Kis szünet, hogy ne terheljük a CPU-t feleslegesen
                continue
            
            # Frissítsük az utolsó olvasás idejét
            last_read_time = time.time()
            
            # Parse time information
            match = pattern.search(line)
            if match and duration and progress_callback:
                hours, minutes, seconds = map(float, match.groups())
                current_time = hours * 3600 + minutes * 60 + seconds
                progress_percent = min(100, (current_time / duration) * 100)
                
                # Calculate estimated time remaining
                elapsed_time = time.time() - start_time
                if progress_percent > 0:
                    estimated_total_time = elapsed_time * (100 / progress_percent)
                    remaining_seconds = max(0, estimated_total_time - elapsed_time)
                else:
                    remaining_seconds = 0
                
                # Túl sok ideig 32% körül van? Csak figyeljük, de nem szakítjuk meg
                if 31 <= progress_percent <= 33:
                    # Debug üzenet a konzolon, de hagyjuk folytatni
                    pass
                
                # Update progress not too frequently to avoid GUI overload
                current_time = time.time()
                if current_time - last_update_time > 0.5:  # Update every 0.5 seconds
                    try:
                        progress_callback(progress_percent, remaining_seconds, current_time)
                    except Exception as e:
                        print(f"Warning: Progress callback error: {e}")
                    last_update_time = current_time
        
        # Get return code
        return_code = process.poll()
        
        # Várjunk a stderr olvasó szál befejezésére
        stderr_thread.join(timeout=5)
        
        # Összegyűjtjük a stderr teljes tartalmát
        error_output = ''.join(stderr_lines)
        
        # Final progress update
        if progress_callback and return_code == 0:
            try:
                progress_callback(100, 0, time.time())
            except Exception as e:
                print(f"Warning: Final progress callback error: {e}")
        
        if return_code == 0:
            print("Conversion completed successfully!")
            return True
        else:
            print(f"Error during conversion with return code {return_code}")
            print(f"FFmpeg error output: {error_output}")
            return False
            
    except Exception as e:
        print(f"Error during conversion: {e}")
        traceback.print_exc()  # Részletes hiba információ
        return False


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(description="Convert video files to MPG format with specific parameters.")
    parser.add_argument("input", help="Input video file path")
    parser.add_argument("-o", "--output", help="Output MPG file path (optional)")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output file if it exists")
    parser.add_argument("-r", "--resolution", default="720x576", help="Output resolution (default: 720x576)")
    parser.add_argument("-q", "--quality", default="medium", 
                        choices=["low", "medium", "high", "veryhigh", "ultra", "maximum"], 
                        help="Video quality preset (default: medium)")
    args = parser.parse_args()
    
    # Check if FFmpeg is installed
    if not check_ffmpeg():
        sys.exit(1)
    
    # Define a simple progress callback for CLI
    def print_progress(percent, remaining, _):
        remaining_min = int(remaining // 60)
        remaining_sec = int(remaining % 60)
        print(f"\rProgress: {percent:.1f}% - Estimated time remaining: {remaining_min}m {remaining_sec}s", end="")
    
    # Perform the conversion
    success = convert_to_mpg(args.input, args.output, args.overwrite, args.resolution, print_progress, args.quality)
    print()  # New line after progress
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()