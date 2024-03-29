"""mediaScout_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
import api.views as views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.mediaScout.as_view(), name="mediascout"),

    path("api/auth/login", views.authView.login),
    path("api/auth/logout", views.authView.logout),
    path("api/auth/perm", views.authView.permissions),

    path("api/user/get", views.userView.get),
    path("api/user/add", views.userView.add),
    path("api/user/edit", views.userView.edit),
    path("api/user/delete", views.userView.delete),

    path("api/user/youtube/check/<str:channel_id>", views.youtubeView.check),
    path("api/user/youtube/get/<int:user_id>", views.youtubeView.get),
    path("api/user/youtube/mutate/<int:user_id>", views.youtubeView.mutate),
    
    path("api/user/youtube/get/<int:youtube_id>/videos", views.videoView.get),
    path("api/user/youtube/videos/download/<int:video_id>", views.videoView.download),
    path("api/user/youtube/get/<int:youtube_id>/videos/download_all", views.videoView.download_all),
]

