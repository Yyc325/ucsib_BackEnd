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

@csrf_exempt
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
            service.noticeCreate(title, subtitle, content, publisher, status, publish_time, cover)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            logger.error(f"Error creating: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'invalid method'}, status=405)


@csrf_exempt
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