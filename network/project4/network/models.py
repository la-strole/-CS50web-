from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    pass


class Post(models.Model):
    id = models.UUIDField(editable=False, primary_key=True, default=uuid.uuid4)
    post_text = models.TextField()
    author = models.ForeignKey("User", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(editable=False)
    like_count = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.author}:{self.post_text}"
