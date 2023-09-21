from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime
User = get_user_model()
# Create your models here.
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.IntegerField()
    bio = models.TextField(max_length=100, blank=True)
    profileimg = models.ImageField(upload_to='profile_images', default='img.png', blank=True)
    location = models.TextField(blank=True)
class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.CharField(max_length=100)
    img = models.ImageField(upload_to='post_images')
    caption = models.TextField()
    created_time = models.TimeField(default=datetime.now)
    no_of_like = models.IntegerField(default=0)
class Like_post(models.Model):
    id_port = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
class Followcount(models.Model):
    follower = models.CharField(max_length=100)
    user = models.CharField(max_length=100)

