from config import ENABLE_WECHAT, ENABLE_DINGTALK
from api.cc98_api import fetch_hot_topics
from database.db_utils import update_database
from database.models import create_tables
from utils.ding_talk import send_ding
from utils.wechat_notify import send_wechat
from utils.post_parser import fetch_LZ_markdown, fetch_and_store_hot_comments
from utils.log_utils import put_log

def main():
    
    try:
        create_tables()
    except Exception as e:
        put_log(f"连接数据库表失败: {e}")
        return

    put_log("获取 CC98 热门话题...")
    hot_topics = fetch_hot_topics()

    if hot_topics:
        put_log("获取成功，更新数据库")
        new_posts, statistics = update_database(hot_topics)

        try:
            fetch_and_store_hot_comments()
        except Exception as e:
            put_log(f"获取热评失败: {e}")

        if new_posts:
            put_log("新增的主题: " + str(new_posts))

            # 展示当前十大
            content = "## CC98 当前十大\n\n"
            for post in hot_topics:
                pastTitle = "原标题："+post['pastTitle'] if post['pastTitle'] else ""
                content += f"- 【{post['boardName']}】【{post['hitCount']}浏览 {post['replyCount']}回复】[{post['title']}](https://www.cc98.org/topic/{post['id']}){pastTitle}\n"

            # 展示新晋十大
            content += "\n## 新晋十大详细信息\n"
            for cnt, (id, title, board) in enumerate(new_posts, start=1):
                content += f"\n{cnt}. **[【{board}】{title}](https://www.cc98.org/topic/{id})**\n\n"
                content += fetch_LZ_markdown(id, statistics[id])

            # 发送钉钉和企业微信通知
            if ENABLE_DINGTALK: send_ding("CC98 十大更新", content)
            if ENABLE_WECHAT: send_wechat("CC98 十大更新", content)
    else:
        put_log("未获取到数据")

if __name__ == "__main__":
    main()