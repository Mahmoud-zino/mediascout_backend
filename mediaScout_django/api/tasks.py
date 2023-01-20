import os
import django
from celery import shared_task
from pytube import YouTube

# important to run the code only when models are loaded
django.setup()
from api.youtube import get_all_new_channel_videos, download_youtube_video
from api.models import YoutubeData, YoutubeVideo


@shared_task
def download_new_videos(new_video_ids: set):
    for video_id in new_video_ids:
        download_youtube_video(video_id)

# TODO: Activate shared_task before deploying
@shared_task
def update_youtube_videos():

    youtube_records = YoutubeData.objects.all()

    for youtube_record in youtube_records:
        existing_video_ids = set(YoutubeVideo.objects.filter(
            youtube_data__channel_id=youtube_record.channel_id).values_list('video_id', flat=True))
        new_video_ids = get_all_new_channel_videos(
            youtube_record.channel_id, existing_video_ids)

        for video_id in new_video_ids:
            yt = YouTube(
                f"https://www.youtube.com/watch?v={video_id}")
            yt_obj = YoutubeVideo.objects.create(video_id=video_id, youtube_data_id=youtube_record.id, 
             title=yt.title, length=yt.length, publish_date=yt.publish_date.strftime("%Y-%m-%d %H:%M:%S"))

            yt_obj.save()

        download_new_videos.apply_async()
