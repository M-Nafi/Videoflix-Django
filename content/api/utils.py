import os
import subprocess
from PIL import Image
from moviepy import VideoFileClip


def convert_video(input_path: str, output_path: str, resolution: int) -> None:
    """
    Convert a video to a specified vertical resolution using ffmpeg.

    Args:
        input_path (str): Path to the source video file.
        output_path (str): Path where the converted video will be saved.
        resolution (int): Target height in pixels for the output video.
    """
    height = resolution
    command = [
        "ffmpeg",
        "-i", input_path,
        "-vf", f"scale=-2:{height}",
        "-c:v", "libx264",
        "-crf", "23",
        "-preset", "fast",
        "-c:a", "aac",
        "-movflags", "+faststart",
        output_path,
    ]
    subprocess.run(command, check=True)


def convert_video_to_hls(input_path: str, output_dir: str, resolution: int) -> str:
    """
    Convert a video to HLS format with segments for adaptive streaming.

    Args:
        input_path (str): Path to the source video file.
        output_dir (str): Directory where HLS files will be saved.
        resolution (int): Target height in pixels for the output video.

    Returns:
        str: Path to the generated m3u8 playlist file.
    """
    height = resolution
    playlist_path = os.path.join(output_dir, "index.m3u8")
    
    command = [
        "ffmpeg",
        "-i", input_path,
        "-vf", f"scale=-2:{height}",
        "-c:v", "libx264",
        "-crf", "23",
        "-preset", "fast",
        "-c:a", "aac",
        "-hls_time", "10",
        "-hls_list_size", "0",
        "-hls_segment_filename", os.path.join(output_dir, "%03d.ts"),
        playlist_path,
    ]
    subprocess.run(command, check=True)
    return playlist_path


def generate_thumbnail(input_path: str, output_path: str) -> None:
    """
    Generate a thumbnail image for the given video file.

    The thumbnail will be resized to 272x154 pixels and saved at the specified output path.

    Args:
        input_path (str): Path to the source video file.
        output_path (str): Path where the thumbnail image will be saved.
    """
    command = [
        "ffmpeg",
        "-i", input_path,
        "-ss", "00:00:01",  
        "-vframes", "1",     
        "-vf", "scale=272:154",  
        "-update", "1",      
        "-y", 
        output_path
    ]
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        if not os.path.exists(output_path):
            raise Exception(f"Thumbnail was not created at {output_path}")
        print(f"DEBUG: Thumbnail created successfully at {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: FFmpeg failed to create thumbnail: {e.stderr}")
        raise


def get_hls_manifest_by_resolution(video, resolution: str):
    """
    Retrieve the HLS manifest file field corresponding to the given resolution.

    Args:
        video: Video model instance containing different HLS manifest fields.
        resolution (str): Resolution key ('480p', '720p', '1080p').

    Returns:
        The HLS manifest file corresponding to the resolution or None if not found.
    """
    manifest_map = {
        '480p': video.hls_480p_manifest,
        '720p': video.hls_720p_manifest,
        '1080p': video.hls_1080p_manifest,
    }
    return manifest_map.get(resolution)


def get_hls_segment_path(video, resolution: str, segment_filename: str) -> str:
    """
    Get the file system path for an HLS segment.

    Args:
        video: Video model instance.
        resolution (str): Resolution key ('480p', '720p', '1080p').
        segment_filename (str): Name of the segment file (e.g., '000.ts').

    Returns:
        str: Full path to the segment file or None if not found.
    """
    manifest = get_hls_manifest_by_resolution(video, resolution)
    if not manifest:
        return None
    
    manifest_dir = os.path.dirname(manifest.path)
    segment_path = os.path.join(manifest_dir, segment_filename)
    
    if os.path.exists(segment_path):
        return segment_path
    return None