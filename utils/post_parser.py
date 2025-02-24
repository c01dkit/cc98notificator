import re
import os
import subprocess
import time
from datetime import datetime
from PIL import Image
from config import ENABLE_LLM_ABSTRACT, ABSTRACT_THRESHOLD
from api.cc98_api import fetch_post, fetch_hot_comments
from api.llm_api import invoke_llm
from utils.oss_utils import upload_to_oss
from utils.time_utils import calculate_time_difference
from utils.log_utils import put_log
from database.db_utils import store_comments, fetch_query

def download_image(url, save_dir="./pictures", wait=2):
    """下载图片并转换格式"""
    os.makedirs(save_dir, exist_ok=True)
    filename = os.path.join(save_dir, os.path.basename(url))
    command = ["wget", "-q", url, "-O", filename]

    try:
        png_file = filename.replace('webp', 'png')
        if not os.path.exists(png_file):
            time.sleep(wait)
            subprocess.run(command, check=True)
            with Image.open(filename) as img:
                img.save(png_file, "png")
            os.remove(filename)
        return png_file
    except subprocess.CalledProcessError:
        return None

def upload_image(filename):
    """上传图片到 OSS 并返回 URL"""
    object_name = os.path.basename(filename)
    return upload_to_oss(filename, object_name)

def convert_img_tags(text):
    """转换 [img]URL[/img] 为 Markdown 格式，并下载图片"""
    img_pattern = re.compile(r'\[img\](.*?)\[/img\]'
                             r'|!\[(.*?)\]\((https?:[^\s]+webp).*?\)', re.IGNORECASE | re.DOTALL)
    
    def replace_match(match):
        url = match.group(1) or match.group(3)
        local_path = download_image(url)
        if local_path:
            remote_url = upload_image(local_path)
            return f"![{os.path.basename(local_path)}]({remote_url})"
        return match.group(0)

    return img_pattern.sub(replace_match, text)

def ubb_quote_to_markdown(text):
    """转换 UBB 引用 [quote] 为 Markdown 引用"""
    if '[quote]' not in text:
        return text

    def get_quote_list(text, quotes):
        current_list = re.findall(r'\[quote\](.*)\[/quote\]', text, re.DOTALL)
        if not current_list:
            return quotes
        quotes.append(current_list[0])
        return get_quote_list(current_list[0], quotes)

    quotes = get_quote_list(text, [])
    current_text = text.replace('[quote]'+ quotes[0] + '[/quote]', '')

    quotes = quotes[::-1]
    new_quotes = [quotes[0]]
    for i in range(1, len(quotes)):
        new_quotes.append(quotes[i].replace('[quote]'+ quotes[i-1] + '[/quote]', ''))

    for ind, quote in enumerate(new_quotes):
        user_match = re.search(r'\[b\]以下是引用(\d+)楼：用户([^\s]+)在.*?的发言：.*?\[/b\]', quote, re.DOTALL)
        if user_match:
            floor = user_match.group(1)
            username = user_match.group(2)
            body = quote[user_match.end():].strip()
        else:
            floor = '?'
            username = '未知用户'
            body = quote.strip()
        new_quotes[ind] = f"> 【{username}（{floor}楼）】：{body}"

    return '\n\n' + '\n\n'.join(new_quotes) + '\n\n' + current_text

def calculate_fengping(awards):
    """计算风评"""
    fengping = 0
    for award in awards:
        if '风评' in award['content']:
            temp = int(award['content'][-2:])
            fengping += temp
    return f"+{fengping}" if fengping > 0 else str(fengping)

def fetch_and_store_hot_comments():
    """获取需要热评的帖子，并存储热评"""
    
    # 查询数据库，获取需要处理的帖子 ID
    query = """
    SELECT id FROM hot_topics_static
    WHERE id NOT IN (SELECT DISTINCT topicId FROM hot_topics_comments)
    AND TIMESTAMPDIFF(HOUR, createTime, NOW()) > 72;
    """
    topic_ids = fetch_query(query)

    if not topic_ids:
        put_log("没有需要获取热评的帖子")
        return
    
    topic_ids = [row[0] for row in topic_ids]

    for topic_id in topic_ids:
        put_log(f"获取 topic {topic_id} 的热评...")
        comments = fetch_hot_comments(topic_id)

        if comments:
            store_comments(topic_id, comments)
        else:
            # 如果没有热评，存储一条默认数据
            default_comment = {
                "id": int(f"{topic_id}000"),
                "topicId": topic_id,
                "parentId": None,
                "boardId": None,
                "userName": "系统",
                "userId": 0,
                "content": "暂无热评",
                "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "ip": "0.0.0.0",
                "state": 0,
                "isAnonymous": False,
                "floor": 0,
                "likeCount": 0,
                "dislikeCount": 0,
                "isLZ": False
            }
            store_comments(topic_id, [default_comment])
            put_log(f"Topic {topic_id} 没有热评，已插入默认数据")

def fetch_LZ_markdown(post_id, post_statistics):
    """获取帖子详情并转为 Markdown 格式"""
    first_10 = fetch_post(post_id)
    if not first_10:
        return "无法获取帖子内容"

    data = first_10[0]
    raw_content = data['content']

    try:
        store_comments(post_id, [data])  # 存储楼主的首帖
    except Exception as e:
        put_log(f"存储评论失败: {e}")

    lz = f"匿名{data['userName'].upper()}" if data['isAnonymous'] else data['userName']

    try:
        data['content'] = convert_img_tags(data['content']) 
        time.sleep(10)
    except Exception as e:
        put_log(f"图片处理失败: {e}")
        pass
    
    # 计算各种统计数据
    data['content'] = data['content'].replace('\n', '\n\n')
    hours, minutes = calculate_time_difference(data['time'])
    top10_timecost = f"{hours}小时{minutes}分钟"
    fengping = calculate_fengping(data['awards'])
    simple_time = data['time'].split('T')[0] + ' ' + data['time'].split('T')[1].split('.')[0]
    participant = post_statistics['participantCount']
    reply = post_statistics['replyCount']
    hit = post_statistics['hitCount']
    content = f"""**楼主**：{lz}\n\n**发表时间**：{simple_time}\n\n**赞**：{data['likeCount']} **踩**：{data['dislikeCount']} **累计风评**：{fengping}\n\n**浏览量**：{hit}\n\n**回帖量**：{reply} **回帖人数**：{participant}\n\n**进入十大用时**：{top10_timecost}\n\n"""

    # 处理引用、图片，调用LLM总结超长帖子
    raw_content = ubb_quote_to_markdown(raw_content)
    raw_content = re.sub(r'\[img\].*?\[/img\]', '', raw_content, flags=re.DOTALL).strip()
    real_text = ubb_quote_to_markdown(data['content'])
    if ENABLE_LLM_ABSTRACT and len(raw_content) > ABSTRACT_THRESHOLD:
        try:
            llm_abstract = invoke_llm("在校内论坛上，有人发了下面这个帖子。请概括内容，150字左右："+raw_content)
            content += f"""**Deepseek总结**：\n\n{llm_abstract}\n\n"""
        except:
            content += f"""**Deepseek总结**：服务器繁忙，请稍后重试 :)\n\n"""
            pass
    content += f"""**帖子原文内容**：\n\n{real_text}\n\n"""

    # 补充热评
    try:
        hotcomments = fetch_hot_comments(post_id)
        if hotcomments:
            content += "**热评**：\n\n"
            for comment in hotcomments:
                if comment['isAnonymous']:
                    user = '匿名' + comment['userName'].upper()
                else:
                    user = comment['userName']
                real_text = ubb_quote_to_markdown(comment['content'])
                content += f"- **【{user}（{comment['floor']}楼）{comment['likeCount']}赞{comment['dislikeCount']}踩】**：{real_text}\n"
    except Exception as e:
        put_log(f"获取热评失败: {e}")
    return content