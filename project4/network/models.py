from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    following = models.ManyToManyField("User", blank=True)

    def serialize(self):
        return {
            "following": [user.id for user in self.following.all()]
    }

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.CharField(max_length=255)
    likes = models.IntegerField(default=0)
    liked_by = models.ManyToManyField(User, blank=True, related_name="liked")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post by {self.user}: {self.content}"

    def serialize(self):
        return {
            "id": self.id,
            "content": self.content,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
            "likes": self.likes,
            "liked_by": [user.id for user in self.liked_by.all()],
            "user": self.user.id
    }

