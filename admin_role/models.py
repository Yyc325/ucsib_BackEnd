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

class Notice(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)
    content = models.TextField()
    publisher = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    publish_time = models.DateTimeField()
    create_time = models.DateTimeField(auto_now_add=True)
    # cover = models.CharField(max_length=255)
    cover = models.CharField(max_length=255, null=True, blank=True)  # 存储七牛云 URL
    position_index = models.CharField(max_length=255)
    publish_location = models.CharField(max_length=255)

    user = models.ForeignKey('Admin', on_delete=models.CASCADE, related_name='notices')

    class Meta:
        db_table = 'admin_notice_copy1'  # 指定数据库表


