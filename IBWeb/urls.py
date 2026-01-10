"""
URL configuration for IBWeb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
# from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # 1. 核心路由：处理前端发来的 /api/...
    # 这会匹配 /api/admin_role/... 和 /api/comments/...
    path("", include("community.urls")),
    path("api/admin_role/", include('admin_role.urls')),
    path("api/", include("community.urls")),

    # 2. 容错路由：如果前端 Axios 拼出了 /api/api/...
    # 这一行是解决你日志中出现 /api/api/ 错误的关键补丁
    path("api/api/admin_role/", include('admin_role.urls')),
    path("api/api/", include("community.urls")),
]
