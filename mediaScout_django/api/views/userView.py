import json
from django.http import JsonResponse

from api.models import User
from api.serializers import UserSerializer
from django.forms import ValidationError


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
