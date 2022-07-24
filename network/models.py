from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post_user")
    text = models.TextField(blank=True, max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    likecount = models.IntegerField(default=0)

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user,
            "text": self.text,
            "timestamp": self.timestamp,
            "likecount": self.likecount
        }
#     comments = models.ManyToManyField("comment", related_name="post_comments", blank=True)
    
# class Comment(models.Model):
#     user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="comment_user")
#     text = models.TextField(max_length=127)
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user}:/n{self.text}"

class Following(models.Model):
    follower = models.ForeignKey("User", on_delete=models.CASCADE, related_name="follower_user", default=None)
    following = models.ForeignKey("User", on_delete=models.CASCADE, related_name="following_user", default=None)

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, default=None)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)