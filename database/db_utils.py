import pymysql
from datetime import datetime
from config import DB_CONFIG
from utils.log_utils import put_log

def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)

def execute_query(query, params=None):
    """执行数据库更新操作"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params or ())
    conn.commit()
    cursor.close()
    conn.close()

def fetch_query(query, params=None):
    """执行查询操作"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params or ())
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result

def store_comments(topic_id, comments:list):
    """存储帖子热评到数据库"""
    if not comments:
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()

    insert_query = """
    INSERT INTO hot_topics_comments (
        id, topicId, parentId, boardId, userName, userId, content, time, ip, state,
        isAnonymous, floor, likeCount, dislikeCount, isLZ
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    comment_data = [
        (
            comment['id'], comment['topicId'], comment['parentId'], comment['boardId'],
            comment['userName'], comment['userId'], comment['content'], comment['time'],
            comment['ip'], comment['state'], comment['isAnonymous'], comment['floor'],
            comment['likeCount'], comment['dislikeCount'], comment['isLZ']
        )
        for comment in comments
    ]

    cursor.executemany(insert_query, comment_data)
    conn.commit()
    put_log(f"已存储 topic {topic_id} 的 {len(comments)} 条评论")
    cursor.close()
    conn.close()

def update_database(hot_topics):
    """
    更新数据库，并返回新增的 ID 与统计数据
    """
    statistics = {}
    conn = get_db_connection()
    cursor = conn.cursor()

    new_topic = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for topic in hot_topics:
        topic_id = topic["id"]
        title = topic["title"]
        board_id = topic["boardId"]
        board_name = topic["boardName"]
        participant_count = topic["participantCount"]
        reply_count = topic["replyCount"]
        hit_count = topic["hitCount"]
        author_user_id = topic["authorUserId"]
        is_anonymous = topic["isAnonymous"]
        create_time = topic["createTime"]

        # 更新统计信息
        statistics[topic_id] = {
            "participantCount": participant_count,
            "replyCount": reply_count,
            "hitCount": hit_count,
            "pastTitles": '',
        }

        # 检查该 ID 是否已存在
        cursor.execute("SELECT id FROM hot_topics_static WHERE id=%s", (topic_id,))
        exists = cursor.fetchone()

        if not exists:
            # 如果 id 不存在，插入到静态信息表
            cursor.execute("""
                INSERT INTO hot_topics_static (id, boardName, title, authorUserId, isAnonymous, createTime)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (topic_id, board_name, title, author_user_id, is_anonymous, create_time))

            new_topic.append((topic_id, title, board_name))

        # 检查标题是否变化
        cursor.execute("SELECT title FROM hot_topics_static WHERE id=%s ORDER BY updateTime DESC LIMIT 1", (topic_id,))
        last_title = cursor.fetchone()

        if last_title and last_title[0] != title:
            # 标题发生变化，记录到 title_changes 表
            cursor.execute("""
                INSERT INTO hot_topics_title_changes (id, old_title, new_title)
                VALUES (%s, %s, %s)
            """, (topic_id, last_title[0], title))
            # 同步更新静态信息表
            cursor.execute("UPDATE hot_topics_static SET title=%s WHERE id=%s", (title, topic_id))
            put_log(f"Topic {topic_id} 标题变化: {last_title[0]} -> {title}")
            statistics[topic_id]["pastTitle"] = last_title[0]
        # 插入当前动态数据
        cursor.execute("""
            INSERT INTO hot_topics_dynamic (id, participantCount, replyCount, hitCount, updateTime)
            VALUES (%s, %s, %s, %s, %s)
        """, (topic_id, participant_count, reply_count, hit_count, now))

    conn.commit()
    cursor.close()
    conn.close()
    return new_topic, statistics