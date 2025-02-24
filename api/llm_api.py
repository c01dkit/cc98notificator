import requests
import re
from config import get_host_ip, LLM_MODEL
from utils.log_utils import put_log

def invoke_llm(content):
    """调用 LLM 生成摘要"""
    res = requests.post(f'http://{get_host_ip()}:11434/api/generate', 
                        json={"model": LLM_MODEL, "prompt": content, "stream": False})
    data = res.json()
    full_text = data['response']
    
    # 移除 <think> 标签及其内容
    full_text = re.sub(r'<think>[\s\S]*?</think>', '', full_text).strip()
    return full_text