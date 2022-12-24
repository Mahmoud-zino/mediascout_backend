from django.db import models
from django.core.validators import URLValidator, MaxLengthValidator, MinLengthValidator

# Create your models here.
class YoutubeData(models.Model):
    id = models.CharField(primary_key=True, max_length=24, null=False, default=None)
    url = models.URLField(validators=[URLValidator], null=False, default=None)
    imageUrl = models.URLField(validators=[URLValidator], null=False, default=None)

class User(models.Model):
    name = models.CharField(max_length=50, null=False, default=None, validators=[
        MaxLengthValidator(50, "NAME_MAX_ERROR"),
        MinLengthValidator(3, "NAME_MIN_ERROR")])
    youtube = models.ForeignKey(YoutubeData, null=True, blank=True, default=None, on_delete=models.CASCADE)