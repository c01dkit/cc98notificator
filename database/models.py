import pymysql
from config import DB_CONFIG

def create_tables():
    """创建数据库表"""
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 创建静态信息表（仅插入新的id）
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hot_topics_static (
        id BIGINT PRIMARY KEY,
        boardName VARCHAR(255),
        title VARCHAR(512),
        authorUserId BIGINT,
        isAnonymous BOOLEAN,
        alreadySent BOOLEAN,
        createTime DATETIME,
        updateTime DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # 创建动态信息表（每次查询插入一条记录）
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hot_topics_dynamic (
        id BIGINT,
        participantCount INT,
        replyCount INT,
        hitCount INT,
        updateTime DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id) REFERENCES hot_topics_static(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # 创建标题变化记录表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hot_topics_title_changes (
        id BIGINT,
        old_title VARCHAR(512),
        new_title VARCHAR(512),
        changeTime DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id) REFERENCES hot_topics_static(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # 创建热评记录表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hot_topics_comments (
        id BIGINT PRIMARY KEY COMMENT '评论 ID',
        topicId BIGINT COMMENT '关联的主题 ID',
        parentId BIGINT COMMENT '父评论 ID（如果是子评论）',
        boardId INT COMMENT '版块 ID',
        userName VARCHAR(255) COMMENT '用户名',
        userId BIGINT COMMENT '用户 ID',
        content TEXT COMMENT '评论内容（允许大文本存储）',
        time DATETIME COMMENT '评论时间',
        ip VARCHAR(45) COMMENT 'IP 地址（部分可能隐藏）',
        state INT COMMENT '状态信息',
        isAnonymous BOOLEAN COMMENT '是否匿名',
        floor INT COMMENT '楼层',
        likeCount INT COMMENT '点赞数',
        dislikeCount INT COMMENT '踩数',
        isLZ BOOLEAN COMMENT '是否为楼主',
        FOREIGN KEY (topicId) REFERENCES hot_topics_static(id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='热门话题的热评记录表';
    """)

    conn.commit()
    cursor.close()
    conn.close()