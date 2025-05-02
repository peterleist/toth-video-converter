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


def convert_to_mpg(input_file, output_file=None, overwrite=False, resolution="720x576", progress_callback=None):
    """
    Convert a video file to MPG format with specific parameters.
    
    Args:
        input_file: Path to the input video file.
        output_file: Path for the output MPG file. If None, derived from input filename.
        overwrite: Whether to overwrite existing output file.
        resolution: Output video resolution as string, e.g. '720x576'.
        progress_callback: Callback function to report progress (value between 0 and 100)
                          and estimated time remaining in seconds.
    
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
    
    print(f"Converting '{input_file}' to '{output_file}' with resolution {resolution}...")
    
    # Get video duration for progress calculation
    duration = get_video_duration(input_file)
    
    # Prepare FFmpeg command with exact parameters from the reference file
    # Changed -sample_fmt s32 to s16 as MP2 codec only supports s16
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", input_file,
        "-c:v", "mpeg2video",        # MPEG-1/2 Video codec
        "-s", resolution,            # Resolution from parameter
        "-r", "25",                  # Frame rate 25 fps
        "-pix_fmt", "yuv420p",       # Planar 4:2:0 YUV
        "-c:a", "mp2",               # MPEG Audio Layer 1/2
        "-ar", "48000",              # Audio sample rate 48000 Hz
        "-b:a", "224k",              # Audio bitrate 224 kb/s
        "-ac", "2",                  # Stereo channels
        "-sample_fmt", "s16",        # 16-bit samples (MP2 codec only supports s16)
        "-f", "mpeg",                # Force MPEG format
        "-progress", "-",            # Output progress information to stdout
        "-y" if overwrite else "-n", # Overwrite if flag is set
        output_file
    ]
    
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
        
        # Read output line by line
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            
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
                
                # Update progress not too frequently to avoid GUI overload
                current_time = time.time()
                if current_time - last_update_time > 0.5:  # Update every 0.5 seconds
                    progress_callback(progress_percent, remaining_seconds, current_time)
                    last_update_time = current_time
        
        # Get return code
        return_code = process.wait()
        
        # Final progress update
        if progress_callback:
            progress_callback(100, 0, time.time())
        
        if return_code == 0:
            print("Conversion completed successfully!")
            return True
        else:
            error_output = process.stderr.read()
            print(f"Error during conversion with return code {return_code}")
            print(f"FFmpeg error output: {error_output}")
            return False
            
    except Exception as e:
        print(f"Error during conversion: {e}")
        return False


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(description="Convert video files to MPG format with specific parameters.")
    parser.add_argument("input", help="Input video file path")
    parser.add_argument("-o", "--output", help="Output MPG file path (optional)")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output file if it exists")
    parser.add_argument("-r", "--resolution", default="720x576", help="Output resolution (default: 720x576)")
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
    success = convert_to_mpg(args.input, args.output, args.overwrite, args.resolution, print_progress)
    print()  # New line after progress
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()