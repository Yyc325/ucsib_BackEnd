import hashlib
import datetime
from itertools import groupby
from operator import itemgetter

import jwt
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection, transaction
from django.forms import model_to_dict

from admin_role.models import Admin, Students, Teacher, Subject, Class, Score, Timetable

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