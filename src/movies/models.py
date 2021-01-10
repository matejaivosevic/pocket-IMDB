from django.db import models
import uuid
from src.users.models import User
from bitfield import BitField

class Genre(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, null=False)

class Movie(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, null=False)
    description = models.CharField(max_length=200, null=False)
    image_url = models.CharField(max_length=200, null=True)
    visit_count = models.IntegerField(default=0)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)


class Likes(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = BitField(flags=(0, 1))
