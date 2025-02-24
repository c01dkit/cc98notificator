import requests
import json
from config import WECHAT_WEBHOOK_KEY
from utils.log_utils import put_log

def send_wechat(title, content):
    """
    通过企业微信群机器人 Webhook 发送 Markdown 消息
    """
    headers = {"Content-Type": "application/json"}
    content = f"**{title}**\n\n{content}"
    
    # 截断过长消息
    too_long = False
    content = f"**{title}**\n\n{content}"
    while len(content.encode("utf-8")) > 4096:
        too_long = True
        content = content[:-100]
    if too_long:
        content = content + "……\n【因消息过长，已截断】"

    data = {
        "msgtype": "markdown",
        "markdown": {
            "content": content
        }
    }

    response = requests.post(f'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={WECHAT_WEBHOOK_KEY}', 
                             headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        result = response.json()
        if result["errcode"] == 0:
            put_log("消息推送到企业微信成功！")
        else:
            put_log(f"消息推送失败: {result}")
    else:
        put_log(f"企业微信推送失败，HTTP 状态码: {response.status_code}")