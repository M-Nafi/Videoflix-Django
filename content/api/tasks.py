import os
from django.conf import settings
from content.models import Video
from django_rq import job

from .utils import convert_video_to_hls, generate_thumbnail


@job
def process_video(video_id):
    """Background job to process uploaded video by converting to multiple resolutions and generating HLS streams."""
    
    try:
        video = Video.objects.get(id=video_id)
    except Video.DoesNotExist:
        print(f"ERROR: Video with ID {video_id} does not exist. Task aborted.")
        return
    
    if not video.original_file:
        print(f"ERROR: Video {video_id} has no original_file. Task aborted.")
        return
    
    input_path = video.original_file.path
    base_filename = os.path.splitext(os.path.basename(input_path))[0]
    media_root = settings.MEDIA_ROOT
    
    _convert_hls_streams(video, input_path, base_filename, media_root)
    _generate_video_thumbnail(video, input_path, base_filename, media_root)
    
    video.save()


def _convert_hls_streams(video, input_path: str, base_filename: str, media_root: str):
    """Convert video to HLS streams for adaptive streaming."""
    
    resolutions = [480, 720, 1080]
    for res in resolutions:
        hls_dir = os.path.join(media_root, f'videos/hls/{res}p/{base_filename}')
        os.makedirs(hls_dir, exist_ok=True)
        
        manifest_path = convert_video_to_hls(input_path, hls_dir, res)
        relative_manifest_path = os.path.relpath(manifest_path, media_root)
        setattr(video, f'hls_{res}p_manifest', relative_manifest_path)


def _generate_video_thumbnail(video, input_path: str, base_filename: str, media_root: str):
    """Generate thumbnail image for the video."""
    
    thumbnail_path = os.path.join(
        media_root, f'videos/thumbnails/{base_filename}.jpg')
    os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
    generate_thumbnail(input_path, thumbnail_path)
    video.thumbnail = f'videos/thumbnails/{base_filename}.jpg'
