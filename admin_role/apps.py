from django.apps import AppConfig

class AdminRoleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_role'

    def ready(self): #ready() 是 AppConfig 的生命周期钩子方法，在 Django 应用启动完成（所有应用加载后）时自动调用。
        # 在 Django 启动时启动线程
        from admin_role.autoNotify import start_publish_thread
        start_publish_thread()
