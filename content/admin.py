from django.contrib import admin
from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Admin interface for the Video model with HLS streaming support."""
    
    list_display = ('title', 'genre', 'upload_date', 'has_thumbnail', 'hls_status')
    search_fields = ('title', 'description', 'genre')
    list_filter = ('genre', 'upload_date')
    ordering = ('-upload_date',)
    
    fieldsets = (
        ('Basic Video Information', {
            'fields': ('title', 'description', 'genre')
        }),
        ('File Upload', {
            'fields': ('original_file',),
            'description': 'Upload your original video file. Processing will start automatically.'
        }),
        ('Generated Content', {
            'fields': ('thumbnail',),
            'classes': ('collapse',),
            'description': 'Automatically generated thumbnail'
        }),
        ('Standard Video Files', {
            'fields': ('video_480p', 'video_720p', 'video_1080p'),
            'classes': ('collapse',),
            'description': 'Standard MP4 files in different resolutions (auto-generated)'
        }),
        ('HLS Streaming Files', {
            'fields': ('hls_480p_manifest', 'hls_720p_manifest', 'hls_1080p_manifest'),
            'classes': ('collapse',),
            'description': 'HLS manifest files for adaptive streaming (auto-generated)'
        }),
        ('Metadata', {
            'fields': ('upload_date',),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('upload_date',)

    def thumbnail_preview(self, obj):
        """Show thumbnail preview in admin."""
        if obj.thumbnail:
            return f'<img src="{obj.thumbnail.url}" style="max-height: 50px; max-width: 100px;" />'
        return "No thumbnail"
    thumbnail_preview.allow_tags = True
    thumbnail_preview.short_description = 'Preview'
    
    def file_size(self, obj):
        """Display original file size."""
        if obj.original_file:
            try:
                size = obj.original_file.size
                if size < 1024*1024:
                    return f"{size/1024:.1f} KB"
                elif size < 1024*1024*1024:
                    return f"{size/(1024*1024):.1f} MB"
                else:
                    return f"{size/(1024*1024*1024):.1f} GB"
            except:
                return "Unknown"
        return "No file"
    
    def has_thumbnail(self, obj):
        """Check if video has a thumbnail."""
        return bool(obj.thumbnail)
    has_thumbnail.boolean = True
    has_thumbnail.short_description = 'Thumbnail'
    
    def hls_status(self, obj):
        """Show HLS processing status."""
        hls_fields = [obj.hls_480p_manifest, 
                    obj.hls_720p_manifest, obj.hls_1080p_manifest]
        processed_count = sum(1 for field in hls_fields if field)
        
        if processed_count == 0:
            return "Pending"
        elif processed_count == 3:
            return "Complete"
        else:
            return f"Partial ({processed_count}/3)"
    
    def get_queryset(self, request):
        """Optimize queryset for admin list view."""
        return super().get_queryset(request).select_related()
    
    actions = ['reprocess_hls']
    
    def reprocess_hls(self, request, queryset):
        """Reprocess HLS for selected videos."""
        from .api.tasks import process_video
        
        count = 0
        for video in queryset:
            process_video.delay(video.id)
            count += 1
        
        self.message_user(
            request, 
            f'{count} video(s) queued for HLS reprocessing.'
        )
    reprocess_hls.short_description = "Reprocess HLS for selected videos"
