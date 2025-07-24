from django.shortcuts import render
import json

from django.dispatch.dispatcher import logger
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone

from admin_role import service


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


def add_notice(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        title = data.get('title')
        subtitle = data.get('subtitle')
        content = data.get('content')
        publisher = data.get('publisher')
        status = data.get('status')
        publish_time = data.get('publishTime')
        cover = data.get('cover')

        try:
            user_id = service.get_user_id_by_publisher(publisher)
            service.noticeCreate(title, subtitle, content, publisher, status, publish_time, cover, user_id)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            logger.error(f"Error creating: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'invalid method'}, status=405)


def query_notice(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            phone = data.get('phone', '')
            publisher = data.get('publisher', '')
            teh_info = service.noticeQuery(publisher, phone)
            if teh_info:
                return JsonResponse({'status': 'success', 'data': teh_info})
            return JsonResponse({'status': 'false'})
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
            notice_json = json.loads(request.body)
            notice_id = notice_json.get('id')
            update_data = {
                'title': notice_json.get('title'),
                'subtitle': notice_json.get('subtitle'),
                'content': notice_json.get('content'),
                'publisher': notice_json.get('publisher'),
                'status': notice_json.get('status'),
                'publishTime': notice_json.get('publishTime'),
                'cover': notice_json.get('cover'),
            }
            update_data = {k: v for k, v in update_data.items() if v is not None}
            notice = service.update_notice(notice_id, **update_data)
            return JsonResponse({'status': 'success', 'data': notice})
        except Exception as e:
            logger.error(f"Error updating notice: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'invalid method'}, status=405)

# 删除通知
def notice_delete(request):
    if request.method == 'POST':
        try:
            notice_json = json.loads(request.body)
            notice_id = notice_json.get('id')
            result = service.delete_notice(notice_id)
            if result:
                return JsonResponse({'status': 'success'})
            return JsonResponse({'status': 'false'})
        except Exception as e:
            logger.error(f"Error deleting notice: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'invalid method'}, status=405)

# 撤回通知
def notice_withdraw(request):
    if request.method == 'POST':
        try:
            notice_json = json.loads(request.body)
            notice_id = notice_json.get('id')
            if not notice_id or not str(notice_id).isdigit():
                return JsonResponse({'status': 'error', 'message': '无效的 ID'}, status=400)
            notice_id = int(notice_id)
            notice = service.withdraw_notice(notice_id)
            return JsonResponse({'status': 'success', 'data': notice})
        except Exception as e:
            logger.error(f"Error withdrawing notice: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'invalid method'}, status=405)