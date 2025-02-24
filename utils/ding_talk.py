import time
import hmac
import base64
import hashlib
import urllib.parse
import requests
from config import DINGTALK_CONFIGS
from utils.log_utils import put_log

def get_sign(secret):
    timestamp = str(round(time.time() * 1000))
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return sign, timestamp

def send_ding(title, content):
    for config in DINGTALK_CONFIGS:
        if config['enable']:
            tag = config['tag']
            secret = config['secret']
            access_token = config['access_token']
            sign, timestamp = get_sign(secret)
            webhook = f'https://oapi.dingtalk.com/robot/send?access_token={access_token}&timestamp={timestamp}&sign={sign}'
            
            headers = {'Content-Type': 'application/json'}
            data = {
                "msgtype": "markdown",
                "markdown": {"title": title, "text": content},
                "at": {"isAtAll": False}
            }
            oneline_log = content.replace('\n', ' ')
            put_log(f"向 {tag} 发送钉钉消息: {oneline_log[-300:]}")
            requests.post(webhook, headers=headers, json=data)

    