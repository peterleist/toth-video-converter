#!/usr/bin/env python3
'''
Batch Video Converter Script

This script converts multiple video files to MPG format using FFmpeg.
It can process all video files in a directory or specific files provided by the user.
'''

import os
import sys
import argparse
from pathlib import Path
from video_converter import check_ffmpeg, convert_to_mpg

# Common video file extensions
VIDEO_EXTENSIONS = [
    '.mp4', '.MP4', '.avi', '.AVI', '.mkv', '.MKV', '.mov', '.MOV',
    '.wmv', '.WMV', '.flv', '.FLV', '.webm', '.WEBM'
]

def get_video_files(directory, recursive=False):
    """
    Get all video files in the specified directory.
    
    Args:
        directory: Directory to scan for video files.
        recursive: Whether to scan subdirectories.
    
    Returns:
        list: List of paths to video files.
    """
    video_files = []
    
    if recursive:
        # Walk through all subdirectories
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if any(file_path.endswith(ext) for ext in VIDEO_EXTENSIONS):
                    video_files.append(file_path)
    else:
        # Only scan the specified directory
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path) and any(file.endswith(ext) for ext in VIDEO_EXTENSIONS):
                video_files.append(file_path)
    
    return video_files

def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(description="Convert multiple video files to MPG format.")
    parser.add_argument("-d", "--directory", help="Directory containing video files")
    parser.add_argument("-f", "--files", nargs='+', help="Specific video files to convert")
    parser.add_argument("-r", "--recursive", action="store_true", help="Scan directory recursively")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output files if they exist")
    parser.add_argument("-o", "--output-dir", help="Output directory for converted files")
    args = parser.parse_args()
    
    # Check if FFmpeg is installed
    if not check_ffmpeg():
        sys.exit(1)
    
    # Get the list of video files to convert
    files_to_convert = []
    
    if args.files:
        # Use the specified files
        files_to_convert = [f for f in args.files if os.path.isfile(f)]
        not_found = set(args.files) - set(files_to_convert)
        if not_found:
            print(f"Warning: The following files were not found: {', '.join(not_found)}")
    
    elif args.directory:
        # Get files from the directory
        if os.path.isdir(args.directory):
            files_to_convert = get_video_files(args.directory, args.recursive)
            print(f"Found {len(files_to_convert)} video files in {args.directory}")
        else:
            print(f"Error: Directory '{args.directory}' not found.")
            sys.exit(1)
    
    else:
        # Use current directory as default
        files_to_convert = get_video_files(".", False)
        print(f"Found {len(files_to_convert)} video files in current directory")
    
    if not files_to_convert:
        print("No video files found to convert.")
        sys.exit(1)
    
    # Convert each file
    successful = 0
    failed = 0
    
    for file in files_to_convert:
        # Determine output file path
        if args.output_dir:
            # Create output directory if it doesn't exist
            if not os.path.exists(args.output_dir):
                os.makedirs(args.output_dir)
            
            # Use the same filename but in the output directory
            input_path = Path(file)
            output_file = os.path.join(args.output_dir, input_path.with_suffix('.mpg').name)
        else:
            # Output to the same directory as the input file
            output_file = None
        
        # Convert the file
        if convert_to_mpg(file, output_file, args.overwrite):
            successful += 1
        else:
            failed += 1
    
    # Print summary
    print(f"\nConversion Summary:")
    print(f"  Total: {len(files_to_convert)}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")

if __name__ == "__main__":
    main()