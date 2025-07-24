import hashlib
import datetime
from itertools import groupby
from operator import itemgetter

import jwt
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.forms import model_to_dict

from admin_role.models import Admin, Notice

current_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def create_admin(user_name, real_name, phone, password):
    password = md5_hash(password)
    create_time = current_time
    if Admin.objects.filter(phone=phone).exists():
        raise Exception('手机号已注册')
    Admin.objects.create(
        user_name=user_name,
        real_name=real_name,
        identity='student',
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


def getIdentity(phone):
    admin = Admin.objects.get(phone=phone)
    return admin.identity


def account_all(name, phone):
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
        admin_list = [model_to_dict(admin, exclude=['password']) for admin in admins]

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


def identity_authorization(phone, identity):
    valid_identities = {"admin", "teacher", "student", "parent"}
    if identity not in valid_identities:
        raise Exception(f"身份值错误: {identity}. 参考值： {valid_identities}")

    try:
        user = Admin.objects.get(phone=phone)
        user.identity = identity
        user.save()
        return True  # 更新成功
    except ObjectDoesNotExist:
        return False

# 创建
def noticeCreate(title, subtitle, content, publisher, status, publish_time, cover, user_id):
    create_time = current_time
    Notice.objects.create(
        title=title,
        subtitle=subtitle,
        content=content,
        publisher=publisher,
        status=status,
        publish_time=publish_time,
        cover=cover,
        create_time=create_time,  # 使用Django的timezone.now()获取当前时间
        user_id=user_id
    )

# 根据 publisher 查找 user_id
def get_user_id_by_publisher(publisher):
    try:
        admin = Admin.objects.get(real_name=publisher)
        return admin.id
    except Admin.DoesNotExist:
        raise Exception(f"Admin with real_name '{publisher}' does not exist")

# 查询
def noticeQuery(publisher, phone):
    try:
        # 构建查询条件
        query_conditions = {}

        if publisher:
            query_conditions['publisher__icontains'] = publisher  # 对管理员名字进行模糊查询
        if phone:
            try:
                admin = Admin.objects.get(phone=phone)  # 通过 phone 查找 Admin
                query_conditions['user_id'] = admin.id  # 根据找到的 Admin 的 id 来设置 user_id 查询条件
            except ObjectDoesNotExist:
                return []  # 如果没有找到对应的 Admin，返回空列表

        # 执行查询
        admins = Notice.objects.filter(**query_conditions)

        # 将查询结果转换为字典
        admin_list = [model_to_dict(admin) for admin in admins]

        # 返回 JSON 响应
        return admin_list
    except Exception as e:
        # 处理异常，返回错误响应
        raise Exception(e)

# 获取通知列表
def get_all_notices(title=None, status=None):
    """获取所有通知，支持按标题和状态过滤"""
    try:
        query_conditions = {}
        if title:
            query_conditions['title__icontains'] = title
        if status:
            query_conditions['status'] = status
        notices = Notice.objects.filter(**query_conditions)
        notice_list = [model_to_dict(notice) for notice in notices]
        return notice_list
    except Exception as e:
        raise Exception(f"获取通知失败: {e}")

# 修改通知
def update_notice(notice_id, **kwargs):
    """更新通知"""
    try:
        notice = Notice.objects.get(id=notice_id)
        for key, value in kwargs.items():
            if hasattr(notice, key):
                setattr(notice, key, value)
        notice.save()
        return model_to_dict(notice)
    except ObjectDoesNotExist:
        raise Exception("通知不存在")
    except Exception as e:
        raise Exception(f"更新通知失败: {e}")

# 删除通知
def delete_notice(notice_id):
    """删除通知"""
    try:
        notice = Notice.objects.get(id=notice_id)
        notice.delete()
        return True
    except ObjectDoesNotExist:
        raise Exception("通知不存在")
    except Exception as e:
        raise Exception(f"删除通知失败: {e}")

# 撤回通知
def withdraw_notice(notice_id):
    try:
        notice = Notice.objects.get(id=int(notice_id))
        if notice.status != '已发布':
            raise Exception("仅可撤回已发布通知")
        notice.status = '已撤回'
        notice.save()
        return model_to_dict(notice)
    except ObjectDoesNotExist:
        raise Exception("通知不存在")
    except Exception as e:
        raise Exception(str(e))