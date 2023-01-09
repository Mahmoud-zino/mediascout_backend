import json
from django.forms import ValidationError
from django.http import HttpResponse, JsonResponse, QueryDict
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login, logout
from api.models import User
from api.serializers import UserSerializer
from django.middleware import csrf
from django.views.decorators.csrf import csrf_exempt

class mediaScout(TemplateView):
    template_name = "index.html"


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