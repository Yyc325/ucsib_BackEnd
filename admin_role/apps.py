import sys
from django.apps import AppConfig

class AdminRoleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_role'

    def ready(self):
        # 只有在运行 runserver 时才启动线程
        # 避免在执行 migrate, makemigrations, shell 等命令时启动线程导致报错
        if 'runserver' in sys.argv:
            # 建议放在 ready 内部 import，防止循环导入问题
            from admin_role.autoNotify import start_publish_thread
            print("Starting publish notification thread...")
            start_publish_thread()
