import jwt
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

from admin_role import service
from admin_role.models import Admin

# myapp/middleware.py

SECRET_KEY = 'abcdasdfasd1243'


class SimpleMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        # 需要放行的路径
        self.paths_to_exempt = [
            '/api/admin_role/login',
            '/api/admin_role/admin_add',
            '/api/admin_role/test_add',
            '/api/admin_role/notices/published_by_location'
        ]

    def __call__(self, request):
        if request.path in self.paths_to_exempt:
            return self.get_response(request)

        token = request.headers.get('Admin-Token')
        if token:
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                user_info = payload.get('user_info')
                user_id = user_info.get("id")
                try:
                    user = Admin.objects.get(id=user_id)  # 获取用户实例
                    request.current_admin = user  # 将用户实例添加到请求对象上
                except Admin.DoesNotExist:
                    return JsonResponse({'error': 'Invalid token'}, status=401)
            except jwt.ExpiredSignatureError:
                return JsonResponse({'error': 'Token has expired'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'error': 'Invalid token'}, status=401)
        else:
            return JsonResponse({'status': '用户未登录'}, status=405)

        response = self.get_response(request)
        return response
