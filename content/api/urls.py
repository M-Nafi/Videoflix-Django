from django.urls import path

from .views import (
    VideoUploadView, 
    VideoListView, 
    HLSManifestView,
    HLSSegmentView
)

urlpatterns = [
    path('upload/', VideoUploadView.as_view(), name='video-upload'),
    path('video/', VideoListView.as_view(), name='video-list'),
    path('video/<int:movie_id>/<str:resolution>/index.m3u8', HLSManifestView.as_view(), name='hls-manifest'),
    path('video/<int:movie_id>/<str:resolution>/<str:segment>/', HLSSegmentView.as_view(), name='hls-segment'),
]