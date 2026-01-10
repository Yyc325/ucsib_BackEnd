from django.db import models

# Create your models here.

class Comment(models.Model):
    content = models.TextField()
    author = models.CharField(max_length=100, default="Anonymous")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"<Comment {self.id}>"