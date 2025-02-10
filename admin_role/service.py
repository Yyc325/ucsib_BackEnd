import hashlib
import datetime
from itertools import groupby
from operator import itemgetter

import jwt
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection, transaction
from django.forms import model_to_dict

from admin_role.models import Admin

current_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def create_admin(user_name, real_name, phone, password):
    password = md5_hash(password)
    create_time = current_time
    if Admin.objects.filter(phone=phone).exists():
        raise Exception('手机号已注册')
    Admin.objects.create(
        user_name=user_name,
        real_name=real_name,
        phone=phone,
        password=password,
        create_time=create_time  # 使用Django的timezone.now()获取当前时间
    )


def md5_hash(password):
    """Convert a password to its MD5 hash."""
    return hashlib.md5(password.encode('utf-8')).hexdigest()


def identity_verification(phone, password, request):
    admin = Admin.objects.get(phone=phone)
    if admin.password != md5_hash(password):
        raise Exception('密码错误')

    admin_data = {
        'id': admin.id,
        'user_name': admin.user_name,
        'real_name': admin.real_name,
        'phone': admin.phone,
    }
    return generate_token(admin_data)
    # request.session["user"] = admin.id

def account_all(name,phone):
    try:
        # 构建查询条件
        query_conditions = {}

        if name:
            query_conditions['user_name__icontains'] = name  # 对管理员名字进行模糊查询
        if phone:
            query_conditions['phone__icontains'] = phone  # 对电话号码进行模糊查询

        # 执行查询
        admins = Admin.objects.filter(**query_conditions)

        # 将查询结果转换为字典
        admin_list = [model_to_dict(admin) for admin in admins]

        # 返回 JSON 响应
        return admin_list
    except Exception as e:
        # 处理异常，返回错误响应
        raise Exception(e)

SECRET_KEY = 'abcdasdfasd1243'
EXPIRATION_HOURS = 72


def generate_token(user_info):
    exp_time = datetime.datetime.utcnow() + datetime.timedelta(hours=EXPIRATION_HOURS)
    payload = {
        'user_info': user_info,  # 将 admin_data 放入 payload
        'exp': exp_time  # 设置过期时间
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token