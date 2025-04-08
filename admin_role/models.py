from django.db import models
class Admin(models.Model):
    id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=255)
    real_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=255)
    identity = models.CharField(max_length=255)
    create_time = models.DateTimeField(auto_now=True)
    update_time = models.DateTimeField(auto_now=True)
# Create your models here.
