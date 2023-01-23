import io
import json
from zipfile import ZipFile
from django.forms import ValidationError
from django.http import JsonResponse, StreamingHttpResponse
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login, logout
from api.models import User
from api.serializers import UserSerializer
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build

from api.models import YoutubeData
from api.youtube import youtube_channel_id_valid
from api.tasks import update_youtube_videos, download_new_videos
from api.models import YoutubeVideo

load_dotenv()
service = build('youtube', 'v3', developerKey=os.getenv('API_KEY'))

class mediaScout(TemplateView):
    template_name = "index.html"

class authView():
    def login(request):
        if request.method != "POST":
            return JsonResponse({"Message": "405 Method Not Allowed"}, status=405)

        try:
            params = json.loads(request.body)
            username = params.get('username')
            password = params.get('password')
        except:
            return JsonResponse({"Message":"400 Bad request"},status=400)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse(json.dumps(list(request.user.get_all_permissions())), safe=False, status=200)
        else:
            return JsonResponse({"Message":"401 Unauthorized"},status=401)
    def logout(request):
        if request.method != "GET":
            return JsonResponse({"Message": "405 Method Not Allowed"}, status=405)

        logout(request)
        return JsonResponse({"Message":"200 Logged out"},status=200)

    def permissions(request):
        if request.method != "GET":
            return JsonResponse({"Message": "405 Method Not Allowed"}, status=405)

        return JsonResponse(json.dumps(list(request.user.get_all_permissions())), safe=False, status=200)

class userView():
    def get(request):
        if request.method != "GET":
            return JsonResponse({"Message": "405 Method Not Allowed"}, status=405)

        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return JsonResponse(serializer.data, safe=False, status=200)
        
    def add(request):
        if request.method != "POST":
            return JsonResponse({"Message": "405 Method Not Allowed"}, status=405)

        if not request.user.has_perm('api.add_user'):
            return JsonResponse({"Message":"401 Unauthorized"},status=401)

        try:
            params = json.loads(request.body)
            name = params.get('name')
        except:
            return JsonResponse({"Message":"400 Bad request"},status=400)

        user = User(name=name)

        try:
            user.full_clean()
        except ValidationError:
            return JsonResponse({"Message": "400 Bad request"}, safe=False, status=400)
        else:
            user.save()
        return JsonResponse(UserSerializer(user).data, safe=False, status=200)

    def edit(request):
        if request.method != "PUT":
            return JsonResponse({"Message": "405 Method Not Allowed"}, status=405)

        if not request.user.has_perm('api.change_user'):
            return JsonResponse({"Message":"401 Unauthorized"},status=401)

        try:
            params = json.loads(request.body)
            id = params.get('id')
            name = params.get('name')
        except:
            return JsonResponse({"Message":"400 Bad request"},status=400)
        
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return JsonResponse({"Message":"400 Bad request"},status=400)
            
        user.name = name

        try:
            user.full_clean()
        except ValidationError:
            return JsonResponse({"Message": "400 Bad request"}, safe=False, status=400)
        else:
            user.save()
        return JsonResponse(UserSerializer(user).data, safe=False, status=200)

    def delete(request):
        if request.method != "DELETE":
            return JsonResponse({"Message": "405 Method Not Allowed"}, status=405)

        if not request.user.has_perm('api.delete_user'):
            return JsonResponse({"Message":"401 Unauthorized"},status=401)

        try:
            params = json.loads(request.body)
            id = params.get('id')
        except:
            return JsonResponse({"Message":"400 Bad request"},status=400)
        
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return JsonResponse({"Message":"400 Bad request"},status=400)

        user.delete()
        return JsonResponse({"Message":"200 Deleted User with id: " + str(id)}, status=200)

class youtubeView():
    def check(request, channel_id):
        if request.method != "GET":
            return JsonResponse({"Message": "405 Method Not Allowed"}, status=405)

        if(youtube_channel_id_valid(channel_id)):
            return JsonResponse({"channel_id":channel_id},status=200)
        else:
            return JsonResponse({"Message":"channel_id invalid"},status=200)

    def get(request, user_id):
        if request.method != "GET":
            return JsonResponse({"Message": "405 Method Not Allowed"}, status=405)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({"Message":"400 Bad request"},status=400)

        if user.youtube is None:
            return JsonResponse({ "id": "", "channel_id":"" }, status=200)

        return JsonResponse({ "id": user.youtube.id, "channel_id": user.youtube.channel_id }, status=200)

    def mutate(request, user_id):
        if request.method != "POST":
            return JsonResponse({"Message": "405 Method Not Allowed"}, status=405)

        if not request.user.has_perm('api.add_youtubedata') or not request.user.has_perm('api.delete_youtubedata') or not request.user.has_perm('api.change_youtubedata'):
            return JsonResponse({"Message":"401 Unauthorized"},status=401)

        try:
            user = User.objects.get(id=user_id)
            
            params = json.loads(request.body)
            channel_id = params.get('channel_id')

            if(not youtube_channel_id_valid(channel_id)):
                return JsonResponse({"Message":"channel_id invalid"},status=200)

            if(user.youtube):
                user.youtube.channel_id = channel_id
            else:
                user.youtube = YoutubeData(channel_id = channel_id)
                
            user.youtube.save()
            user.save()

            return JsonResponse({"channel_id":channel_id},status=200)
        except User.DoesNotExist:
            return JsonResponse({"Message":"400 Bad request"},status=400)

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

        file_path = f'{os.path.dirname(os.path.abspath(__file__))}{os.getenv("DATA_PATH")}/{video.video_id}.zip'

        response = StreamingHttpResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{video.title}.zip"'
        response['Content-Type'] = 'application/zip'

        return response

    def download_all(request, youtube_id):
        if request.method != "GET":
            return JsonResponse({"Message": "405 Method Not Allowed"}, status=405)

        try:
            youtube_data = YoutubeData.objects.get(id=youtube_id)
        except YoutubeVideo.DoesNotExist:
            return JsonResponse({"Message":"400 Bad request"},status=400)

        folder_path = f'{os.path.dirname(os.path.abspath(__file__))}{os.getenv("DATA_PATH")}/'
           
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