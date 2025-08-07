import hashlib
import datetime
from itertools import groupby
from operator import itemgetter

import jwt
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.forms import model_to_dict

from admin_role.models import Admin, Notice
from django.utils import timezone

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
    try:
        admin = Admin.objects.get(phone=phone)
        return admin.identity
    except ObjectDoesNotExist:
        return None  # 或者 raise Exception("用户不存在")



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

# 创建通知
def noticeCreate(title, subtitle, content, publisher, status, publish_time, cover_url, user_id, position_index, publish_location='About'):
    """
        创建通知，cover_url 为七牛云返回的 URL
        """
    create_time = current_time #获取当前创建时间
    if not status:  # 默认状态为待发布
        status = '待发布'
    if not publish_time:  # publish_time 为空时，发布时再设置
        publish_time = None
    else:
        try:
            datetime.datetime.strptime(publish_time, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise Exception("发布时间格式错误，应为 %Y-%m-%d %H:%M:%S")
    if publish_location not in ['About', 'News']:
        raise Exception("发布位置必须为 'About' 或 'News'")
    notice = Notice.objects.create( #notice Django ORM 提供的方法，用于在 Notice 模型对应的数据库表中创建新记录。
        title=title,
        subtitle=subtitle,
        content=content,
        publisher=publisher,
        status=status,
        publish_time=publish_time,
        cover=cover_url,  # 存储七牛云 URL
        create_time=create_time,
        user_id=user_id,
        position_index=position_index,
        publish_location = publish_location
    ) #创建并保存记录后返回一个 Notice 实例。 返回的 notice 是一个 Notice 对象，包含所有字段值。
    notice_data = model_to_dict(notice) #model_to_dict()将 notice（Notice 实例）转换为 Python 字典。
    notice_data['create_time'] = timezone.localtime(notice.create_time).strftime("%Y-%m-%d %H:%M:%S") #add

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
        query_conditions = {} #一个空字典，用于动态存储查询条件。

        if publisher:
            query_conditions['publisher__icontains'] = publisher  # 对管理员名字进行模糊查询(不区分大小写) Django 的 icontains 查找器
        if phone:
            try:
                admin = Admin.objects.get(phone=phone)  # 通过 phone 查找 Admin
                query_conditions['user_id'] = admin.id  # 根据找到的 Admin 的 id 来设置 user_id 查询条件
            except ObjectDoesNotExist:
                return []  # 如果没有找到对应的 Admin，返回空列表

        # 执行查询
        admins = Notice.objects.filter(**query_conditions) #使用 Django ORM 查询 Notice 表，应用 query_conditions 中的过滤条件。

        # 将查询结果转换为字典
        # admin_list = [model_to_dict(admin) for admin in admins]
        admin_list = [ #add
            {**model_to_dict(admin),
             'create_time': timezone.localtime(admin.create_time).strftime("%Y-%m-%d %H:%M:%S"),
             'publish_time': timezone.localtime(admin.publish_time).strftime("%Y-%m-%d %H:%M:%S") if admin.publish_time else None}
            for admin in admins
        ]
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
        # notice_list = [model_to_dict(notice) for notice in notices]
        notice_list = [
            {**model_to_dict(notice),
             'create_time': timezone.localtime(notice.create_time).strftime("%Y-%m-%d %H:%M:%S"),
             'publish_time': timezone.localtime(notice.publish_time).strftime("%Y-%m-%d %H:%M:%S") if notice.publish_time else None}
            for notice in notices
        ]
        return notice_list
    except Exception as e:
        raise Exception(f"获取通知失败: {e}")

# 根据电话获取用户
def get_admin_by_phone(phone):
    try:
        return Admin.objects.get(phone=phone)
    except Admin.DoesNotExist:
        raise Exception(f"Admin with phone '{phone}' does not exist")

# 修改通知
def update_notice(notice_id, **kwargs):
    try:
        notice = Notice.objects.get(id=notice_id)
        for key, value in kwargs.items():
            if hasattr(notice, key):
                if key == 'publish_time':
                    if notice.status in ['待发布', '已撤回'] and value:

                        try:
                            value = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                            value = timezone.make_aware(value)
                        except ValueError:
                            raise Exception("发布时间格式错误，应为 %Y-%m-%d %H:%M:%S")

                        setattr(notice, key, value)
                    elif notice.status == '已发布':
                        continue  # 保持原有 publish_time
                elif key == 'publish_location':
                    if notice.status in ['待发布', '已撤回'] and value:
                        if value not in ['About', 'News']:
                            raise Exception("发布位置必须为 'About' 或 'News'")
                        setattr(notice, key, value)
                    elif notice.status == '已发布':
                        continue  # 保持原有 publish_location
                elif key == 'status' and value not in ['待发布', '已撤回', '已发布']:
                    raise Exception("状态值错误，应为 '待发布'、'已撤回' 或 '已发布'")
                else:
                    setattr(notice, key, value)
        notice.save()

        notice_data = model_to_dict(notice, exclude=['password'])
        notice_data['create_time'] = timezone.localtime(notice.create_time).strftime("%Y-%m-%d %H:%M:%S")
        notice_data['publish_time'] = timezone.localtime(notice.publish_time).strftime(
            "%Y-%m-%d %H:%M:%S") if notice.publish_time else None
        return notice_data

        # return model_to_dict(notice)
    except ObjectDoesNotExist:
        raise Exception("通知不存在")
    except Exception as e:
        raise Exception(f"更新通知失败: {e}")

# 删除通知
def delete_notice(notice_id):
    """删除通知，支持单个 ID 或 ID 列表"""
    try:
        # 将输入转换为列表，兼容单个 ID
        if not isinstance(notice_id, (list, tuple)):
            notice_ids = [int(notice_id)] if str(notice_id).isdigit() else []
        else:
            notice_ids = [int(id) for id in notice_id if str(id).isdigit()]

        if not notice_ids:
            raise Exception("无有效通知 ID")

        deleted_count = Notice.objects.filter(id__in=notice_ids).delete()[0]
        if deleted_count == 0:
            raise Exception("未找到要删除的通知")
        return True
    except ObjectDoesNotExist:
        raise Exception("通知不存在")
    except Exception as e:
        raise Exception(f"删除通知失败: {e}")

# 撤回通知
def withdraw_notice(notice_id):
    try:
        # 将输入转换为列表，兼容单个 ID
        if not isinstance(notice_id, (list, tuple)):
            notice_ids = [int(notice_id)] if str(notice_id).isdigit() else []
        else:
            notice_ids = [int(id) for id in notice_id if str(id).isdigit()]

        if not notice_ids:
            raise Exception("无有效通知 ID")

        notices = Notice.objects.filter(id__in=notice_ids, status='已发布')
        updated_notices = []
        for notice in notices:
            notice.status = '已撤回'
            notice.save()
            updated_notices.append(model_to_dict(notice))
        if not updated_notices:
            raise Exception("无符合条件的通知可撤回")
        return updated_notices if len(updated_notices) > 1 else updated_notices[0] if updated_notices else None
    except ObjectDoesNotExist:
        raise Exception("通知不存在")
    except Exception as e:
        raise Exception(str(e))

# 发布通知
def publish_notice(notice_id, current_user_real_name):
    try:
        # 将输入转换为列表，兼容单个 ID
        if not isinstance(notice_id, (list, tuple)):
            notice_ids = [int(notice_id)] if str(notice_id).isdigit() else []
        else:
            notice_ids = [int(id) for id in notice_id if str(id).isdigit()]

        if not notice_ids:
            raise Exception("无有效通知 ID")

        # 获取符合条件的通知（状态为 '待发布' 或 '已发布'）
        notices = Notice.objects.filter(id__in=notice_ids, status__in=['待发布', '已撤回'])
        updated_notices = []
        current_datetime = datetime.datetime.strptime(current_time, "%Y-%m-%d %H:%M:%S")
        current_datetime = timezone.make_aware(current_datetime, timezone.utc).astimezone(timezone.get_current_timezone())

        for notice in notices:
            notice.publisher = current_user_real_name
            notice.publish_time = current_datetime  # 直接设置当前时间，不考虑定时
            notice.status = '已发布'
            notice.user_id = get_user_id_by_publisher(current_user_real_name)  # 关联当前用户
            notice.save()
            updated_notices.append(model_to_dict(notice))

        if not updated_notices:
            raise Exception("无符合条件的通知可发布")
        return updated_notices if len(updated_notices) > 1 else updated_notices[0]
    except ObjectDoesNotExist:
        raise Exception("通知不存在")
    except Exception as e:
        raise Exception(f"发布通知失败: {e}")

#根据发布位置查询已发布通知
def get_published_notices_by_location(publish_location):
    """根据发布位置查询已发布的通知"""
    try:
        if publish_location not in ['About', 'News']:
            raise Exception("发布位置必须为 'About' 或 'News'")

        notices = Notice.objects.filter(
            status='已发布',
            publish_location=publish_location
        )
        notice_list = [
            {
                **model_to_dict(notice),
                'create_time': timezone.localtime(notice.create_time).strftime("%Y-%m-%d %H:%M:%S"),
                'publish_time': timezone.localtime(notice.publish_time).strftime(
                    "%Y-%m-%d %H:%M:%S") if notice.publish_time else None
            }
            for notice in notices
        ]
        return notice_list
    except Exception as e:
        raise Exception(f"查询已发布通知失败: {e}")