import logging
import uuid
from datetime import datetime
import json
from qiniu import Auth, put_stream, BucketManager
from qiniu import set_default
from django.http import JsonResponse
from django.core.exceptions import ValidationError

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 七牛云配置
ACCESS_KEY = "MaHPkigLXOc1Z3Gb2zrIsHxSGYYG11HtrqC-qxFF"  # 替换为您的七牛 Access Key
SECRET_KEY = "_8wwqFOqTe_T_It7gqYegU6i6hjtStkUYoHZOfJy"  # 替换为您的七牛 Secret Key
BUCKET = "xycloud-dida"  # 替换为您的七牛存储空间名称
BASE_URL = "https://niu.xycloud.net.cn/"  # 替换为您的七牛域名


class FileUploadUtil:
    @staticmethod
    def upload(file, path=None, params=None, policy=None):
        """
        上传文件到七牛云
        :param file: Django UploadedFile 对象
        :param path: 文件路径，例如 /excel/APPCODESDK9@@FD213123/2023/9-26/UUID
        :param params: 自定义参数，需以 x: 开头
        :param policy: 上传策略
        :return: 包含上传结果的字典
        """
        try:
            # 初始化七牛认证
            auth = Auth(ACCESS_KEY, SECRET_KEY)

            # 设置上传策略
            if policy is None:
                policy = {
                    "returnBody": '{"key":"$(key)","hash":"$(etag)","fname":"$(x:fname)"}'
                }
            if params is None:
                params = {}
                if file.name:
                    params["x:fname"] = file.name

            # 生成上传凭证
            up_token = auth.upload_token(BUCKET, path, 3600, policy)

            # 如果未提供路径，生成默认路径
            if not path:
                user_model = {"tenant_id": "123", "id": "1234"}  # 假设用户数据
                suffix = f".{file.name.split('.')[-1]}" if file.name else ""
                path = FileUploadUtil.build_path(user_model, suffix)
                # 直接使用 file 作为 input_stream
                input_stream = file
            # 上传文件
            ret, info = put_stream(up_token, path, input_stream,"test.png", file.size)

            if info.status_code == 200:
                result = {
                    "key": ret.get("key"),
                    "hash": ret.get("hash"),
                    "fname": params.get("x:fname"),
                    "url": f"{BASE_URL}{ret.get('key')}"
                }
                logger.info(f"文件上传成功: {result}")
                return result
            else:
                logger.error(f"文件上传失败: {info}")
                raise Exception(f"文件上传失败: {info}")

        except Exception as e:
            logger.error(f"上传文件时发生错误: {str(e)}")
            raise

    @staticmethod
    def delete_file(file_key):
        """
        从七牛云删除文件
        :param file_key: 文件的 key
        :return: 删除是否成功
        """
        try:
            auth = Auth(ACCESS_KEY, SECRET_KEY)
            bucket_manager = BucketManager(auth)
            ret, info = bucket_manager.delete(BUCKET, file_key)
            if info.status_code == 200:
                logger.info(f"文件删除成功: {file_key}")
                return True
            else:
                logger.error(f"文件删除失败: {info}")
                return False
        except Exception as e:
            logger.error(f"删除文件时发生错误: {file_key}, 错误: {str(e)}")
            return False

    @staticmethod
    def build_path(user_model, suffix):
        """
        构建文件路径
        :param user_model: 用户模型，包含 tenant_id 和 id
        :param suffix: 文件后缀
        :return: 构建的文件路径
        """
        date_str = datetime.now().strftime("%Y-%m-%d")
        return (f"knowledge/{user_model.get('tenant_id')}/{user_model.get('id')}/"
                f"{date_str}/{uuid.uuid4().hex.upper()}{suffix}")

    @staticmethod
    def upload_files(files):
        """
        批量上传文件
        :param files: Django UploadedFile 对象列表
        :return: JsonResponse 包含上传结果
        """
        try:
            # 验证文件大小（100MB 限制）
            for file in files:
                if file.size > 100 * 1024 * 1024:
                    logger.warning("单个文件大小不能超过100MB")
                    return JsonResponse({
                        "status": "error",
                        "message": "单个文件大小不能超过100MB"
                    }, status=400)

            start_time = datetime.now()
            logger.info("文件上传接口调用")

            results = []
            policy = {
                "returnBody": '{"key":"$(key)","hash":"$(etag)","fname":"$(x:fname)"}'
            }

            for file in files:
                params = {"x:fname": file.name} if file.name else {}
                user_model = {"tenant_id": "123", "id": "123"}  # 假设用户数据
                suffix = f".{file.name.split('.')[-1]}" if file.name else ""
                path = FileUploadUtil.build_path(user_model, suffix)
                result = FileUploadUtil.upload(file, path, params, policy)
                results.append(result)

            logger.info(f"文件上传接口调用结束，耗时: {(datetime.now() - start_time).total_seconds() * 1000}ms")
            logger.info(f"上传结果: {json.dumps(results)}")
            return JsonResponse({
                "status": "success",
                "data": results
            })

        except Exception as e:
            logger.error(f"批量上传文件时发生错误: {str(e)}")
            return JsonResponse({
                "status": "error",
                "message": f"文件上传错误: {str(e)}"
            }, status=500)