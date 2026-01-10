from django.urls import path
import admin_role.views

urlpatterns = [
    path('admin_add', admin_role.views.add),
    path('login', admin_role.views.login),
    path('account_all', admin_role.views.account_all),
    path('identity_authorization', admin_role.views.identity_authorization),
    path('notices/add', admin_role.views.add_notice),
    path('notices/query', admin_role.views.query_notice),
    path('notices', admin_role.views.notice_list),
    path('notices/update', admin_role.views.notice_update),
    path('notices/delete', admin_role.views.notice_delete),
    path('notices/withdraw', admin_role.views.notice_withdraw),
    path('notices/publish', admin_role.views.publish_notice),
    path('upload_file', admin_role.views.upload_file),  # 新增文件上传路由
    path('notices/published_by_location', admin_role.views.published_notices_by_location),#根据发布位置查询已发布通知



]