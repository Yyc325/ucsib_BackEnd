from django.urls import path

import admin_role.views

urlpatterns = [
    path('admin_add', admin_role.views.add),
    path('login', admin_role.views.login),
]