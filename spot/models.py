from django.db import models

# Create your models here.
class Album(models.Model):
    album = models.TextField(blank=True)

class Artist(models.Model):
    artist = models.TextField(blank=True)

class Song(models.Model):
    song = models.TextField(blank=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
