from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.timezone import timedelta

# Create your models here.
class Movies(models.Model):
    class CATEGORY(models.TextChoices):
        ACTION = 'Action', 'Action'
        DRAMA = 'Drama', 'Drama'
        COMEDY = 'Comedy', 'Comedy'
        HORROR = 'Horror', 'Horror'
        THRILLER = 'Thriller', 'Thriller'
        ROMANCE = 'Romance', 'Romance'
        SCIFI = 'Sci-Fi', 'Sci-Fi'
        DOCUMENTARY='Documentary','Documentary'
    title = models.CharField(max_length=100)
    desc = models.TextField(max_length=500)
    image = models.ImageField(null=True,blank=True,upload_to="posters/")
    video = models.FileField(null=True,blank=True,upload_to="videos/")
    category=models.CharField(choices=CATEGORY.choices,default=CATEGORY.DRAMA,max_length=100,null=True,blank=True)
    rating = models.IntegerField(null=True,blank=True)
    release_date = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    is_premium = models.BooleanField(default=False)
    banner = models.ImageField(null=True,blank=True,upload_to="banners/")

class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    first_name=models.CharField(null=True, max_length=100)
    last_name=models.CharField(null=True, max_length=100)
    email  = models.CharField(null=True, max_length=100)
    image = models.ImageField(null=True,blank=True,upload_to="user_images/")
    
class Type(models.Model):
    name = models.CharField(max_length=100, unique=True)
    movies= models.ManyToManyField(Movies, null=True,blank=True)

    def __str__(self):
        return self.name

class Cast(models.Model):
    name = models.CharField(max_length=100, unique=True)
    movies= models.ManyToManyField(Movies, null=True,blank=True)
    image = models.ImageField(null=True,blank=True,upload_to="cast_images/")

    def __str__(self):
        return self.name
    
class WatchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movies, on_delete=models.CASCADE)
    watched_at = models.DateTimeField(auto_now_add=False,null=True,blank=True)

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movies, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)