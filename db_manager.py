import pymysql
from db_config import DB_CONFIG


class DBManager:
    def __init__(self):
        self.conn = None
        self.cursor = None
        
    def connect(self):
        self.conn = pymysql.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor()
        
    def close(self):
        self.cursor.close()
        self.conn.close()
        
    def insert_note(self, note_data):
        sql = """
        INSERT INTO xhs_notes 
        (note_id, note_url, title, author_name, author_url, publish_time, like_count, keyword)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        note_url = VALUES(note_url),
        title = VALUES(title),
        author_name = VALUES(author_name),
        author_url = VALUES(author_url),
        publish_time = VALUES(publish_time),
        like_count = VALUES(like_count),
        keyword = VALUES(keyword)
        """
        self.cursor.execute(sql, (
            note_data['note_id'],
            note_data['note_url'],
            note_data['title'],
            note_data['author_name'],
            note_data['author_url'],
            note_data['publish_time'],
            note_data['like_count'],
            note_data['keyword']
        ))
        self.conn.commit()
        
    def batch_insert_notes(self, notes_list):
        sql = """
        INSERT INTO xhs_notes
        (note_id, note_url, title, author_name, author_url, publish_time, like_count, keyword, is_comment_crawled)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        note_url = VALUES(note_url),
        title = VALUES(title),
        author_name = VALUES(author_name),
        author_url = VALUES(author_url),
        publish_time = VALUES(publish_time),
        like_count = VALUES(like_count),
        keyword = VALUES(keyword),
        is_comment_crawled = VALUES(is_comment_crawled)
        """
        data_list = [
            (
                note['note_id'],
                note['note_url'],
                note['title'],
                note['author_name'],
                note['author_url'],
                note['publish_time'],
                note['like_count'],
                note['keyword'],
                0  # 默认设置为未爬取
            )
            for note in notes_list
        ]
        self.cursor.executemany(sql, data_list)
        self.conn.commit()
    
    def batch_insert_comments(self, note_id, note_url, comment_list, keyword=None):
        sql = """
        INSERT INTO xhs_comments
        (note_id, note_url, comment_content, keyword)
        VALUES (%s, %s, %s, %s)
        """
        data_list = [
            (note_id, note_url, comment_text, keyword)
            for comment_text in comment_list
        ]
        self.cursor.executemany(sql, data_list)
        self.conn.commit()

    def check_notes_exist(self, note_ids):
        """
        检查note_id是否已存在于数据库中
        :param note_ids: list，要检查的note_id列表
        :return: list，已存在的note_id列表
        """
        if not note_ids:
            return []

        # 构建查询SQL
        placeholders = ','.join(['%s'] * len(note_ids))
        sql = f"SELECT note_id FROM xhs_notes WHERE note_id IN ({placeholders})"

        # 执行查询
        self.cursor.execute(sql, note_ids)
        existing_note_ids = [row[0] for row in self.cursor.fetchall()]

        return existing_note_ids

    def mark_note_as_crawling(self, note_id):
        """
        标记笔记为正在爬取评论
        :param note_id: 笔记ID
        """
        sql = "UPDATE xhs_notes SET is_comment_crawled = 2 WHERE note_id = %s"
        self.cursor.execute(sql, (note_id,))
        self.conn.commit()
        print(f"已标记笔记 {note_id} 为正在爬取")

    def mark_note_as_crawled(self, note_id):
        """
        标记笔记为已爬取评论
        :param note_id: 笔记ID
        """
        sql = "UPDATE xhs_notes SET is_comment_crawled = 1 WHERE note_id = %s"
        self.cursor.execute(sql, (note_id,))
        self.conn.commit()
        print(f"已标记笔记 {note_id} 为已爬取")

    def get_uncrawled_notes(self, limit=10, keyword=None):
        """
        获取未爬取评论的笔记
        :param limit: 限制返回数量
        :param keyword: 可选，指定关键词筛选
        :return: 笔记列表
        """
        if keyword:
            sql = """
            SELECT note_id, note_url, title, author_name, author_url, publish_time, like_count, keyword
            FROM xhs_notes
            WHERE is_comment_crawled = 0 AND keyword = %s
            LIMIT %s
            """
            self.cursor.execute(sql, (keyword, limit))
        else:
            sql = """
            SELECT note_id, note_url, title, author_name, author_url, publish_time, like_count, keyword
            FROM xhs_notes
            WHERE is_comment_crawled = 0
            LIMIT %s
            """
            self.cursor.execute(sql, (limit,))

        columns = ['note_id', 'note_url', 'title', 'author_name', 'author_url', 'publish_time', 'like_count', 'keyword']
        notes = [dict(zip(columns, row)) for row in self.cursor.fetchall()]

        return notes

    def get_crawled_notes_count(self, keyword=None):
        """
        获取已爬取评论的笔记数量
        :param keyword: 可选，指定关键词筛选
        :return: 数量
        """
        if keyword:
            sql = "SELECT COUNT(*) FROM xhs_notes WHERE is_comment_crawled = 1 AND keyword = %s"
            self.cursor.execute(sql, (keyword,))
        else:
            sql = "SELECT COUNT(*) FROM xhs_notes WHERE is_comment_crawled = 1"
            self.cursor.execute(sql)

        return self.cursor.fetchone()[0]
    
    def check_note_replied(self, note_id):
        sql = "SELECT COUNT(*) FROM xhs_note_agent_records WHERE note_id = %s"
        self.cursor.execute(sql, (note_id,))
        count = self.cursor.fetchone()[0]
        return count > 0
    
    def get_note_reply_count(self, note_id):
        sql = "SELECT COUNT(*) FROM xhs_note_agent_records WHERE note_id = %s"
        self.cursor.execute(sql, (note_id,))
        count = self.cursor.fetchone()[0]
        return count
    
    def insert_agent_record(self, record_data):
        sql = """
        INSERT INTO xhs_note_agent_records 
        (note_id, note_title, note_desc, comment_content, reply_text, is_like, reply_bool, reason_text, keyword)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(sql, (
            record_data['note_id'],
            record_data['note_title'],
            record_data['note_desc'],
            record_data['comment_content'],
            record_data['reply_text'],
            record_data['is_like'],
            record_data['reply_bool'],
            record_data['reason_text'],
            record_data.get('keyword', None)
        ))
        self.conn.commit()
    
    def check_note_researched(self, note_id):
        sql = "SELECT COUNT(*) FROM xhs_demand_research_records WHERE note_id = %s"
        self.cursor.execute(sql, (note_id,))
        count = self.cursor.fetchone()[0]
        return count > 0
    
    def insert_demand_research_record(self, record_data):
        sql = """
        INSERT INTO xhs_demand_research_records 
        (note_id, note_title, note_desc, comment_content, is_newcomer, has_launch_intent, 
         demand_level, reply_text, reason, is_like, reply_bool, keyword)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(sql, (
            record_data['note_id'],
            record_data['note_title'],
            record_data['note_desc'],
            record_data['comment_content'],
            record_data['is_newcomer'],
            record_data['has_launch_intent'],
            record_data['demand_level'],
            record_data['reply_text'],
            record_data['reason'],
            record_data['is_like'],
            record_data['reply_bool'],
            record_data.get('keyword', None)
        ))
        self.conn.commit()
    
    def get_high_value_users(self, keyword=None, limit=100):
        if keyword:
            sql = """
            SELECT * FROM xhs_demand_research_records 
            WHERE is_newcomer = 1 AND has_launch_intent = 1 
            AND demand_level IN ('潜在需求', '强需求')
            AND keyword = %s
            ORDER BY reply_time DESC
            LIMIT %s
            """
            self.cursor.execute(sql, (keyword, limit))
        else:
            sql = """
            SELECT * FROM xhs_demand_research_records 
            WHERE is_newcomer = 1 AND has_launch_intent = 1 
            AND demand_level IN ('潜在需求', '强需求')
            ORDER BY reply_time DESC
            LIMIT %s
            """
            self.cursor.execute(sql, (limit,))
        return self.cursor.fetchall()
