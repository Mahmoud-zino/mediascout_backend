import json
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout

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
