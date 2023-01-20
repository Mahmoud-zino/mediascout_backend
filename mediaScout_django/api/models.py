from django.db import models
from django.core.validators import URLValidator, MaxLengthValidator, MinLengthValidator

# Create your models here.

class YoutubeData(models.Model):
    channel_id = models.CharField(max_length=24, null=False, default=None)


class YoutubeVideo(models.Model):
    video_id = models.CharField(max_length=11, null=False, default=None),
    title = models.CharField(max_length=100, null=False, default=None),
    length = models.IntegerField(null=False, default=None),
    publish_date = models.DateTimeField(null=False, default=None)
    youtube_data = models.ForeignKey(YoutubeData, on_delete=models.CASCADE)


class User(models.Model):
    name = models.CharField(max_length=50, null=False, default=None, validators=[
        MaxLengthValidator(50, "NAME_MAX_ERROR"),
        MinLengthValidator(3, "NAME_MIN_ERROR")])
    youtube = models.ForeignKey(YoutubeData, null=True, blank=True, default=None, on_delete=models.CASCADE)