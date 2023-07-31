from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    pass


class Followers(models.Model):
    follower = models.ForeignKey(User, related_name='followed_by_user', on_delete=models.CASCADE)
    followed = models.ForeignKey(User, related_name='followed_by_another', on_delete=models.CASCADE)
    class Meta:
        unique_together = ('follower', 'followed')

class Post(models.Model):
    id = models.UUIDField(editable=False, primary_key=True, default=uuid.uuid4)
    post_text = models.TextField()
    author = models.ForeignKey("User", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(editable=False)
    like_count = models.PositiveSmallIntegerField(default=0)
    unlike_count = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["-timestamp"]
    
    def get_post(self):
        return (
            {
                'postText' : self.post_text,
                'author' : self.author.username,
                'timestamp' : self.timestamp.strftime("%d-%m-%Y %H:%M:%S"),
                'likeCount' : self.like_count,
                'unlikeCount': self.unlike_count
            }
        )
    def __str__(self):
        return f"{self.author}:{self.post_text}"
