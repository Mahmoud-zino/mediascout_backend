import json
from django.http import JsonResponse

from api.youtube import youtube_channel_id_valid
from api.models import User, YoutubeData


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

            return JsonResponse({"id": user.youtube.id, "channel_id":channel_id},status=200)
        except User.DoesNotExist:
            return JsonResponse({"Message":"400 Bad request"},status=400)
