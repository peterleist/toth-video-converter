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


def convert_to_mpg(input_file, output_file=None, overwrite=False, resolution="720x576"):
    """
    Convert a video file to MPG format with specific parameters.
    
    Args:
        input_file: Path to the input video file.
        output_file: Path for the output MPG file. If None, derived from input filename.
        overwrite: Whether to overwrite existing output file.
        resolution: Output video resolution as string, e.g. '720x576'.
    
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
        "-y" if overwrite else "-n", # Overwrite if flag is set
        output_file
    ]
    
    try:
        # Run FFmpeg command
        process = subprocess.run(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        print("Conversion completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during conversion: {e}")
        print(f"FFmpeg error output: {e.stderr}")
        return False


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(description="Convert video files to MPG format with specific parameters.")
    parser.add_argument("input", help="Input video file path")
    parser.add_argument("-o", "--output", help="Output MPG file path (optional)")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output file if it exists")
    args = parser.parse_args()
    
    # Check if FFmpeg is installed
    if not check_ffmpeg():
        sys.exit(1)
    
    # Perform the conversion
    success = convert_to_mpg(args.input, args.output, args.overwrite)
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()