from django.shortcuts import render
import json

from django.dispatch.dispatcher import logger
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone

from admin_role import service
import jwt

from admin_role.file_upload_util import FileUploadUtil



# Create your views here.

def get_admin(request):
    return request.current_admin


@csrf_exempt
def add(request):
    if request.method == 'POST':
        admin_json = json.loads(request.body)
        user_name = admin_json.get('user_name', '')
        real_name = admin_json.get('real_name', '')
        phone = admin_json.get('phone', '')
        password = admin_json.get('password', '')
        try:
            service.create_admin(user_name, real_name, phone, password)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            logger.error(f"Error creating: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'invalid method'}, status=405)


@csrf_exempt
def login(request):
    if request.method == 'POST':
        try:
            admin_json = json.loads(request.body)
            phone = admin_json.get('phone', '')
            password = admin_json.get('password', '')
            token = service.identity_verification(phone, password, request)
            identity = service.getIdentity(phone)
            return JsonResponse({'status': 'success', 'token': token, 'identity': identity})
        except Exception as e:
            logger.error(f"Error creating: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'invalid method'}, status=405)


# Create your views here.

@csrf_exempt
def account_all(request):
    if request.method == 'POST':
        try:
            admin_json = json.loads(request.body)
            phone = admin_json.get('phone', '')
            username = admin_json.get('userName', '')
            teh_info = service.account_all(username, phone)
            if teh_info:
                return JsonResponse({'status': 'success', 'data': teh_info})
            return JsonResponse({'status': 'false'})
        except Exception as e:
            logger.error(f"Error creating: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'invalid method'}, status=405)


@csrf_exempt
def identity_authorization(request):
    if request.method == 'POST':
        try:
            admin_json = json.loads(request.body)
            phone = admin_json.get('phone', '')
            identity = admin_json.get('identity', '')
            teh_info = service.identity_authorization(phone, identity)
            if teh_info:
                return JsonResponse({'status': 'success', 'data': teh_info})
            return JsonResponse({'status': 'false'})
        except Exception as e:
            logger.error(f"Error creating: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'invalid method'}, status=405)

#上传文件
def upload_file(request):
    """
    上传文件到七牛云
    """
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            print("1233333333")#test
            if not token:
                return JsonResponse({'status': 'error', 'message': '缺少 token'}, status=401)
            payload = jwt.decode(token, service.SECRET_KEY, algorithms=['HS256'])
            phone = payload['user_info']['phone'] #从 payload 中提取 user_info.phone
            identity = service.getIdentity(phone)
            if identity != 'admin':
                return JsonResponse({'status': 'error', 'message': '仅管理员有权限'}, status=403)

            file = request.FILES.get('file')
            if not file:
                return JsonResponse({'status': 'error', 'message': '未提供文件'}, status=400)

            # 验证文件类型
            valid_extensions = ['png', 'jpg', 'jpeg']
            file_extension = file.name.split('.')[-1].lower() #从文件名中提取扩展名，转换为小写。
            if file_extension not in valid_extensions:
                return JsonResponse({
                    'status': 'error',
                    'message': f'文件类型不支持，仅支持 {", ".join(valid_extensions)}'
                }, status=400)

            # 验证文件大小（5MB 限制）
            if file.size > 5 * 1024 * 1024:
                return JsonResponse({
                    'status': 'error',
                    'message': '文件大小不能超过5MB'
                }, status=400)

            # 假设用户数据
            user_model = {"tenant_id": "123", "id": str(payload['user_info']['id'])}
            result = FileUploadUtil.upload(file)
            return JsonResponse({'status': 'success', 'data': result})
        except jwt.exceptions.InvalidTokenError:
            return JsonResponse({'status': 'error', 'message': '无效的 token'}, status=401)
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'invalid method'}, status=405)

#创建通知
def add_notice(request):
    if request.method == 'POST':
        try:
            # 获取并验证 token
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not token:
                return JsonResponse({'status': 'error', 'message': '缺少 token'}, status=401)
            payload = jwt.decode(token, service.SECRET_KEY, algorithms=['HS256'])
            phone = payload['user_info']['phone']
            identity = service.getIdentity(phone)

            # 确保用户为管理员
            if identity != 'admin':
                return JsonResponse({'status': 'error', 'message': '仅管理员有权限'}, status=403)

            # 获取当前用户的 publisher
            current_user = service.get_admin_by_phone(phone)
            publisher = current_user.real_name  # 直接使用当前用户的 real_name 作为 publisher

            # 处理请求数据
            data = json.loads(request.body)
            title = data.get('title')
            subtitle = data.get('subtitle')
            content = data.get('content')
            publish_time = data.get('publish_time')
            cover_url = data.get('cover_url')  # 七牛云返回的 URL
            position_index = data.get('position_index')  # 发布位置序号
            publish_location = data.get('publish_location', 'About')  # 默认值为 'About'

            try:
                user_id = service.get_user_id_by_publisher(publisher)  # 获取对应的 user_id
                service.noticeCreate(title, subtitle, content, publisher, None, publish_time, cover_url, user_id, position_index, publish_location)
                return JsonResponse({'status': 'success'})
            except Exception as e:
                logger.error(f"Error creating: {e}")
                return JsonResponse({'status': 'error', 'message': str(e)})
        except jwt.exceptions.InvalidTokenError:
            return JsonResponse({'status': 'error', 'message': '无效的 token'}, status=401)
        except Exception as e:
            logger.error(f"Error creating: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'invalid method'}, status=405)


# 查询通知
def query_notice(request):
    if request.method == 'POST':
        try:
            # 获取并验证 token
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not token:
                return JsonResponse({'status': 'error', 'message': '缺少 token'}, status=401)
            payload = jwt.decode(token, service.SECRET_KEY, algorithms=['HS256'])
            phone = payload['user_info']['phone']
            identity = service.getIdentity(phone)
            if not identity:
                return JsonResponse({'status': 'error', 'message': '用户不存在'}, status=404)
            if identity != 'admin':
                return JsonResponse({'status': 'error', 'message': '仅管理员有权限'}, status=403)

            data = json.loads(request.body)
            phone = data.get('phone', '')
            publisher = data.get('publisher', '')
            teh_info = service.noticeQuery(publisher, phone)
            if teh_info:
                return JsonResponse({'status': 'success', 'data': teh_info})
            return JsonResponse({'status': 'false'})
        except jwt.exceptions.InvalidTokenError:
            return JsonResponse({'status': 'error', 'message': '无效的 token'}, status=401)
        except Exception as e:
            logger.error(f"Error creating: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'invalid method'}, status=405)

# 获取通知列表
def notice_list(request):
    if request.method == 'POST':
        try:
            notice_json = json.loads(request.body)
            title = notice_json.get('title', '')
            status = notice_json.get('status', '')
            notices = service.get_all_notices(title, status)
            return JsonResponse({'status': 'success', 'data': notices})
        except Exception as e:
            logger.error(f"Error fetching notices: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'invalid method'}, status=405)


# 修改通知
def notice_update(request):
    if request.method == 'POST':
        try:
            # 获取并验证 token
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not token:
                return JsonResponse({'status': 'error', 'message': '缺少 token'}, status=401)
            payload = jwt.decode(token, service.SECRET_KEY, algorithms=['HS256'])
            phone = payload['user_info']['phone']

            # 使用 getIdentity 校验身份
            identity = service.getIdentity(phone)
            if identity != 'admin':
                return JsonResponse({'status': 'error', 'message': '仅管理员有权限'}, status=403)

            # 获取当前用户
            current_user = service.get_admin_by_phone(phone)
            current_publisher = current_user.real_name

            # 处理请求数据
            notice_json = json.loads(request.body)
            notice_id = notice_json.get('id')
            update_data = {
                'title': notice_json.get('title'),
                'subtitle': notice_json.get('subtitle'),
                'content': notice_json.get('content'),
                'publisher': notice_json.get('publisher') if notice_json.get('status') in ['待发布','已撤回'] else current_publisher,
                'status': notice_json.get('status'),
                'publish_time': notice_json.get('publish_time'),
                'cover': notice_json.get('cover_url'),
                'position_index': notice_json.get('position_index')if notice_json.get('status') in ['待发布','已撤回'] else None,
                'publish_location': notice_json.get('publish_location') if notice_json.get('status') in ['待发布','已撤回'] else None,
            }
            update_data = {k: v for k, v in update_data.items() if v is not None}

            notice = service.update_notice(notice_id, **update_data)
            return JsonResponse({'status': 'success', 'data': notice})
        except jwt.exceptions.InvalidTokenError:
            return JsonResponse({'status': 'error', 'message': '无效的 token'}, status=401)
        except Exception as e:
            logger.error(f"Error updating notice: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'invalid method'}, status=405)

# 删除通知
def notice_delete(request):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            payload = jwt.decode(token, service.SECRET_KEY, algorithms=['HS256'])
            phone = payload['user_info']['phone']
            identity = service.getIdentity(phone)
            if identity != 'admin':
                return JsonResponse({'status': 'error', 'message': '仅管理员有权限'}, status=403)

            notice_json = json.loads(request.body)
            notice_id = notice_json.get('id')  # 支持单个 ID以及ID列表
            result = service.delete_notice(notice_id)
            if result:
                return JsonResponse({'status': 'success'})
            return JsonResponse({'status': 'false'})
        except jwt.exceptions.InvalidTokenError:
            return JsonResponse({'status': 'error', 'message': '无效的 token'}, status=401)
        except Exception as e:
            logger.error(f"Error deleting notice: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'invalid method'}, status=405)


# 撤回通知
def notice_withdraw(request):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            payload = jwt.decode(token, service.SECRET_KEY, algorithms=['HS256'])
            phone = payload['user_info']['phone']
            identity = service.getIdentity(phone)
            if identity != 'admin':
                return JsonResponse({'status': 'error', 'message': '仅管理员有权限'}, status=403)

            notice_json = json.loads(request.body)
            notice_id = notice_json.get('id')
            notice = service.withdraw_notice(notice_id)
            return JsonResponse({'status': 'success', 'data': notice})
        except jwt.exceptions.InvalidTokenError:
            return JsonResponse({'status': 'error', 'message': '无效的 token'}, status=401)
        except Exception as e:
            logger.error(f"Error withdrawing notice: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'invalid method'}, status=405)

# 发布通知
def publish_notice(request):
    if request.method == 'POST':
        try:
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not token:
                return JsonResponse({'status': 'error', 'message': '缺少 token'}, status=401)
            payload = jwt.decode(token, service.SECRET_KEY, algorithms=['HS256'])
            phone = payload['user_info']['phone']
            identity = service.getIdentity(phone)
            if identity != 'admin':
                return JsonResponse({'status': 'error', 'message': '仅管理员有权限'}, status=403)

            current_user = service.get_admin_by_phone(phone)
            current_publisher = current_user.real_name

            notice_json = json.loads(request.body)
            notice_id = notice_json.get('id')
            notice = service.publish_notice(notice_id, current_publisher)
            return JsonResponse({'status': 'success', 'data': notice})
        except jwt.exceptions.InvalidTokenError:
            return JsonResponse({'status': 'error', 'message': '无效的 token'}, status=401)
        except Exception as e:
            logger.error(f"Error publishing notice: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'invalid method'}, status=405)

# 根据发布位置查询已发布的通知
@csrf_exempt
def published_notices_by_location(request):
    if request.method == 'POST':
        try:
            # 处理请求数据
            data = json.loads(request.body)
            publish_location = data.get('publish_location')
            if not publish_location:
                return JsonResponse({'status': 'error', 'message': '缺少发布位置参数'}, status=400)

            # 查询已发布通知
            notices = service.get_published_notices_by_location(publish_location)
            return JsonResponse({'status': 'success', 'data': notices})
        except jwt.exceptions.InvalidTokenError:
            return JsonResponse({'status': 'error', 'message': '无效的 token'}, status=401)
        except Exception as e:
            logger.error(f"Error fetching published notices: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'invalid method'}, status=405)