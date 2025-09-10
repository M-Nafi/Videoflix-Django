import os
import subprocess
from PIL import Image
from moviepy import VideoFileClip

FFMPEG_PATH = "/usr/bin/ffmpeg"

def convert_video(input_path: str, output_path: str, resolution: int) -> None:

    height = resolution
    command = [
        FFMPEG_PATH,
        "-i", input_path,
        "-vf", f"scale=-2:{height}",
        "-c:v", "libx264",
        "-crf", "23",
        "-preset", "fast",
        "-c:a", "aac",
        "-movflags", "+faststart",
        output_path,
    ]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"DEBUG: Video successfully converted to {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Video conversion failed:\n{e.stderr}")
        raise

def convert_video_to_hls(input_path: str, output_dir: str, resolution: int) -> str:

    height = resolution
    playlist_path = os.path.join(output_dir, "index.m3u8")
    command = [
        FFMPEG_PATH,
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
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"DEBUG: HLS created successfully at {playlist_path}")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: HLS conversion failed:\n{e.stderr}")
        raise
    return playlist_path

def generate_thumbnail(input_path: str, output_path: str) -> None:

    command = [
        FFMPEG_PATH,
        "-i", input_path,
        "-ss", "00:00:01",
        "-vframes", "1",
        "-vf", "scale=272:154",
        "-y",
        output_path
    ]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        if not os.path.exists(output_path):
            raise Exception(f"Thumbnail was not created at {output_path}")
        print(f"DEBUG: Thumbnail created successfully at {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Thumbnail creation failed:\n{e.stderr}")
        raise

def get_hls_manifest_by_resolution(video, resolution: str):

    manifest_map = {
        '480p': video.hls_480p_manifest,
        '720p': video.hls_720p_manifest,
        '1080p': video.hls_1080p_manifest,
    }
    return manifest_map.get(resolution)

def get_hls_segment_path(video, resolution: str, segment_filename: str) -> str:

    manifest = get_hls_manifest_by_resolution(video, resolution)
    if not manifest:
        return None

    manifest_dir = os.path.dirname(manifest.path)
    segment_path = os.path.join(manifest_dir, segment_filename)
    
    if os.path.exists(segment_path):
        return segment_path
    return None