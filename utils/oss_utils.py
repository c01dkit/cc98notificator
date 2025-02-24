import oss2
import time
from config import ALIYUN_OSS_CONFIG

def upload_to_oss(file_path, object_name):
    """上传文件到阿里云 OSS"""
    time.sleep(2)
    auth = oss2.Auth(ALIYUN_OSS_CONFIG["ACCESSKEY_ID"], ALIYUN_OSS_CONFIG["ACCESSKEY_SECRET"])
    bucket = oss2.Bucket(auth, ALIYUN_OSS_CONFIG["ENDPOINT"], ALIYUN_OSS_CONFIG["BUCKET_NAME"])
    bucket.put_object_from_file(object_name, file_path)
    return f"https://{ALIYUN_OSS_CONFIG['BUCKET_NAME']}.{ALIYUN_OSS_CONFIG['ENDPOINT']}/{object_name}"