from django.contrib import admin

# Register your models here.
# 新增代码
from django.contrib import admin
from .models import Notice

admin.site.register(Notice)