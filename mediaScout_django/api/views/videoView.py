import io
import os
from zipfile import ZipFile
from django.http import JsonResponse, StreamingHttpResponse
from api.models import YoutubeData, YoutubeVideo
from django.conf import settings

class videoView():
    def get(request, youtube_id):
        if request.method != "GET":
            return JsonResponse({"Message": "405 Method Not Allowed"}, status=405)

        if not YoutubeData.objects.filter(id=youtube_id):
            return JsonResponse({"Message":"400 Bad request"},status=400)

        videos = YoutubeVideo.objects.filter(youtube_data_id=youtube_id)

        return JsonResponse({ "videos": list(videos.values()) }, status=200)

    def download(request, video_id):
        if request.method != "GET":
            return JsonResponse({"Message": "405 Method Not Allowed"}, status=405)

        try:
            video = YoutubeVideo.objects.get(id=video_id)
        except YoutubeVideo.DoesNotExist:
            return JsonResponse({"Message":"400 Bad request"},status=400)

        file_path = f'{settings.BASE_DIR}/api/{os.getenv("DATA_PATH")}/{video.video_id}.zip'

        response = StreamingHttpResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{video.video_id}.zip"'
        response['Content-Type'] = 'application/zip'

        return response

    def download_all(request, youtube_id):
        if request.method != "GET":
            return JsonResponse({"Message": "405 Method Not Allowed"}, status=405)

        try:
            youtube_data = YoutubeData.objects.get(id=youtube_id)
        except YoutubeVideo.DoesNotExist:
            return JsonResponse({"Message":"400 Bad request"},status=400)

        folder_path = f'{settings.BASE_DIR}/api/{os.getenv("DATA_PATH")}/'
           
        videos = YoutubeVideo.objects.filter(youtube_data_id=youtube_id)

        in_memory_zip = io.BytesIO()

        with ZipFile(in_memory_zip, "w") as zip:
            for video in videos:
                file_path = os.path.join(folder_path, f'{video.video_id}.zip')
                zip.write(file_path, f'{video.video_id}.zip')

        # Reset the file pointer to the start of the file
        in_memory_zip.seek(0)

        response = StreamingHttpResponse(in_memory_zip, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{youtube_data.channel_id}.zip"'
        return response