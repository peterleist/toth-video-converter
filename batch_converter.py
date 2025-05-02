#!/usr/bin/env python3
'''
Batch Video Converter Script

This script converts multiple video files to MPG format using FFmpeg.
It can process all video files in a directory or specific files provided by the user.
'''

import os
import sys
import argparse
import time
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

def format_time(seconds):
    """Format seconds into a human-readable time string."""
    if seconds < 60:
        return f"{int(seconds)}s"
    
    minutes = int(seconds / 60)
    sec = int(seconds % 60)
    
    if minutes < 60:
        return f"{minutes}m {sec}s"
    
    hours = int(minutes / 60)
    min_rem = int(minutes % 60)
    
    return f"{hours}h {min_rem}m {sec}s"

def progress_callback(percent, remaining_seconds, current_time):
    """Display progress information for the current conversion."""
    progress_bar_length = 40
    filled_length = int(progress_bar_length * percent / 100)
    
    # Create the progress bar
    bar = '█' * filled_length + '░' * (progress_bar_length - filled_length)
    
    # Format the remaining time
    remaining_str = format_time(remaining_seconds)
    
    # Print the progress bar and info
    print(f"\r[{bar}] {percent:.1f}% - ETA: {remaining_str}", end='')

def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(description="Convert multiple video files to MPG format.")
    parser.add_argument("-d", "--directory", help="Directory containing video files")
    parser.add_argument("-f", "--files", nargs='+', help="Specific video files to convert")
    parser.add_argument("-r", "--recursive", action="store_true", help="Scan directory recursively")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite output files if they exist")
    parser.add_argument("-o", "--output-dir", help="Output directory for converted files")
    parser.add_argument("--resolution", default="720x576", help="Output resolution (default: 720x576)")
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
    
    # Track total progress
    total_files = len(files_to_convert)
    start_time = time.time()
    
    for index, file in enumerate(files_to_convert):
        # Display file progress
        file_name = os.path.basename(file)
        print(f"\nFile {index+1}/{total_files}: {file_name}")
        
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
        
        # Convert the file with progress reporting
        if convert_to_mpg(file, output_file, args.overwrite, args.resolution, progress_callback):
            successful += 1
        else:
            failed += 1
        
        # Calculate overall progress
        elapsed = time.time() - start_time
        files_per_sec = (index + 1) / elapsed if elapsed > 0 else 0
        eta = (total_files - (index + 1)) / files_per_sec if files_per_sec > 0 else 0
        overall_progress = ((index + 1) / total_files) * 100
        
        print(f"\nOverall progress: {overall_progress:.1f}% - {index+1}/{total_files} files")
        if eta > 0:
            print(f"Estimated time remaining: {format_time(eta)}")
    
    # Print summary
    total_time = time.time() - start_time
    print(f"\nConversion Summary:")
    print(f"  Total: {total_files}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")
    print(f"  Total time: {format_time(total_time)}")

if __name__ == "__main__":
    main()