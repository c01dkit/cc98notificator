import time
import hmac
import base64
import hashlib
import urllib.parse
import requests
from config import DINGTALK_SECRET, DINGTALK_ACCESS_TOKEN
from utils.log_utils import put_log

def get_sign():
    timestamp = str(round(time.time() * 1000))
    secret_enc = DINGTALK_SECRET.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, DINGTALK_SECRET)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return sign, timestamp

def send_ding(title, content):
    sign, timestamp = get_sign()
    webhook = f'https://oapi.dingtalk.com/robot/send?access_token={DINGTALK_ACCESS_TOKEN}&timestamp={timestamp}&sign={sign}'
    
    headers = {'Content-Type': 'application/json'}
    data = {
        "msgtype": "markdown",
        "markdown": {"title": title, "text": content},
        "at": {"isAtAll": False}
    }
    oneline_log = content.replace('\n', ' ')
    put_log(f"发送钉钉消息: {oneline_log[-300:]}")
    requests.post(webhook, headers=headers, json=data)