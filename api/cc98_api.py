import requests
import os
import time
from config import HEADERS, TOKEN_FILE, USER, PASSWORD
from utils.log_utils import put_log

# 致谢：https://www.cc98.org/topic/5292711
def get_access_token():
    url = "https://openid.cc98.org/connect/token"
    data = {
        "client_id": "9a1fd200-8687-44b1-4c20-08d50a96e5cd",
        "client_secret": "8b53f727-08e2-4509-8857-e34bf92b27f2",
        "grant_type": "password",
        "username": USER,
        "password": PASSWORD
    }
    
    response = requests.post(url, data=data)
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")
        if access_token:
            token_str = f"Bearer {access_token}"
            # 将 token 保存到文件
            with open(TOKEN_FILE, "w", encoding="utf8") as f:
                f.write(token_str)
            return token_str
        else:
            raise ValueError("Access token not found in response.")
    else:
        raise RuntimeError("Failed to get token")

def read_cached_token():
    """读取缓存的 access_token"""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r", encoding="utf8") as f:
            return f.read().strip()
    return None

def fetch_cc98_api(url, need_auth=True, wait=3):
    """获取 CC98 API 数据，自动处理 access_token 的缓存和更新"""
    headers = HEADERS.copy()

    time.sleep(wait)
    if need_auth:
        token = read_cached_token()
        if not token:
            token = get_access_token()
        headers["Authorization"] = token

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 401:
        put_log("Token 过期，正在重新获取...")
        token = get_access_token()
        headers["Authorization"] = token
        time.sleep(wait)
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
    
    put_log(f"请求失败: {response.status_code}")
    return None

def fetch_hot_topics():
    """获取十大热搜数据"""
    return fetch_cc98_api("https://api.cc98.org/config/index", need_auth=False).get('hotTopic', [])

def fetch_hot_comments(topic_id: int):
    """获取某个帖子的热评"""
    return fetch_cc98_api(f"https://api.cc98.org/Topic/{topic_id}/hot-post")

def fetch_post(post_id: int):
    """获取指定帖子的前十楼"""
    return fetch_cc98_api(f"https://api.cc98.org/Topic/{post_id}/post?from=0&size=10")