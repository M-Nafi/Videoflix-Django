import os
import subprocess
from PIL import Image
from moviepy import VideoFileClip

FFMPEG_PATH = "/usr/bin/ffmpeg"

def convert_video(input_path: str, output_path: str, resolution: int) -> None:
    """
    Convert the video at the given input_path to the given output_path,
    downscaled to the given resolution.

    The output video will have the same aspect ratio as the input, but
    with the given height and a width that is scaled accordingly.

    The output video will use the H.264 video codec and the AAC audio codec,
    with a quality of 23 (out of 51, where lower numbers are higher quality
    but larger files).

    The output video will have the "-movflags +faststart" option, which
    allows the video to start playing more quickly (but makes the file
    slightly larger).

    Raises a subprocess.CalledProcessError if the conversion fails.
    """
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
    subprocess.run(command, check=True)


def convert_video_to_hls(input_path: str, output_dir: str, resolution: int) -> str:
    """
    Convert the video at the given input_path to HLS format, scaled to the
    given resolution, and save the output to the given output_dir.

    The output video will have the same aspect ratio as the input, but
    with the given height and a width that is scaled accordingly.

    The output video will use the H.264 video codec and the AAC audio codec,
    with a quality of 23 (out of 51, where lower numbers are higher quality
    but larger files).

    The output video will have the "-hls_time 10" option, which means each
    segment of the video will be 10 seconds long.

    The output video will have the "-hls_list_size 0" option, which means
    the playlist will not be limited to a certain number of segments.

    The output video will have the "-hls_segment_filename" option, which
    specifies the filename for each segment of the video.

    The return value is the path to the playlist file.

    Raises a subprocess.CalledProcessError if the conversion fails.
    """
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
    subprocess.run(command, check=True)
    return playlist_path


def generate_thumbnail(input_path: str, output_path: str) -> None:
    """
    Generate a thumbnail image for the given video input_path, saving it to output_path.

    The thumbnail is created by taking a single frame from the video 1 second in,
    and scaling it to a resolution of 272x154.

    Raises a subprocess.CalledProcessError if the thumbnail creation fails.

    :param input_path: The path to the video file to generate a thumbnail from.
    :param output_path: The path to save the thumbnail image to.
    """
    command = [
        FFMPEG_PATH,
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
    Return the path to the HLS manifest file for the given video and resolution.

    The path is determined by looking up the resolution in a map of
    '480p', '720p', and '1080p' resolutions to the corresponding
    hls_manifest field on the video object.

    If the video does not have an HLS manifest for the given resolution,
    None is returned.

    :param video: The Video object to get the manifest for.
    :param resolution: The resolution to get the manifest for.
    :return: The path to the manifest, or None.
    """
    manifest_map = {
        '480p': video.hls_480p_manifest,
        '720p': video.hls_720p_manifest,
        '1080p': video.hls_1080p_manifest,
    }
    return manifest_map.get(resolution)


def get_hls_segment_path(video, resolution: str, segment_filename: str) -> str:
    """
    Return the path to the HLS segment file for the given video, resolution, and segment filename.

    The path is determined by looking up the resolution in a map of
    '480p', '720p', and '1080p' resolutions to the corresponding
    hls_manifest field on the video object, and then joining that path
    with the given segment filename.

    If the video does not have an HLS manifest for the given resolution,
    or if the segment does not exist, None is returned.

    :param video: The Video object to get the segment for.
    :param resolution: The resolution to get the segment for.
    :param segment_filename: The filename of the segment to get the path for.
    :return: The path to the segment, or None.
    """
    manifest = get_hls_manifest_by_resolution(video, resolution)
    if not manifest:
        return None
    
    manifest_dir = os.path.dirname(manifest.path)
    segment_path = os.path.join(manifest_dir, segment_filename)
    
    if os.path.exists(segment_path):
        return segment_path
    return None