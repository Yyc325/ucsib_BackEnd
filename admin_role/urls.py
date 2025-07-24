from django.urls import path

import admin_role.views

urlpatterns = [
    path('admin_add', admin_role.views.add),
    path('login', admin_role.views.login),
    path('account_all', admin_role.views.account_all),
    path('identity_authorization', admin_role.views.identity_authorization),
    path('notice/add/', admin_role.views.add_notice),
    path('notice/query/', admin_role.views.query_notice),
]