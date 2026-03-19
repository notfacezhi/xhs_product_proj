"""
小红书监控后端服务
提供笔记和评论的API接口
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime
import pymysql

from db_config import DB_CONFIG

app = FastAPI(
    title="小红书监控服务",
    description="提供笔记和评论数据的API接口",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)


@app.get("/")
def read_root():
    """根路径"""
    return {
        "service": "小红书监控服务",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/xhs_craw/stats")
def get_stats():
    """
    获取爬取状态统计
    返回：未爬取、正在爬取、已完成的笔记数量
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 统计各种状态的笔记数量
        stats = {
            "not_crawled": 0,      # 未爬取
            "crawling": 0,         # 正在爬取
            "completed": 0,        # 已完成
            "total": 0
        }

        # 查询各状态数量
        cursor.execute("""
            SELECT
                COUNT(CASE WHEN is_comment_crawled = 0 THEN 1 END) as not_crawled,
                COUNT(CASE WHEN is_comment_crawled = 2 THEN 1 END) as crawling,
                COUNT(CASE WHEN is_comment_crawled = 1 THEN 1 END) as completed,
                COUNT(*) as total
            FROM xhs_notes
        """)
        row = cursor.fetchone()

        if row:
            stats["not_crawled"] = row[0] or 0
            stats["crawling"] = row[1] or 0
            stats["completed"] = row[2] or 0
            stats["total"] = row[3] or 0

        # 查询评论总数
        cursor.execute("SELECT COUNT(*) FROM xhs_comments")
        stats["total_comments"] = cursor.fetchone()[0] or 0

        # 查询最新的爬取时间
        cursor.execute("""
            SELECT MAX(update_time) as last_crawl_time
            FROM xhs_notes
            WHERE is_comment_crawled = 1
        """)
        last_time = cursor.fetchone()[0]
        stats["last_crawl_time"] = last_time.strftime("%Y-%m-%d %H:%M:%S") if last_time else None

        return stats

    finally:
        cursor.close()
        conn.close()


@app.get("/xhs_craw/notes")
def get_notes(
    keyword: Optional[str] = Query(None, description="关键词筛选"),
    status: Optional[str] = Query(None, description="状态筛选: crawling(爬取中), completed(已完成)"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量")
):
    """
    获取笔记列表
    支持关键词筛选、状态筛选、分页
    只返回状态为1(已完成)和2(正在爬取)的笔记
    """
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        # 构建查询条件
        where_conditions = ["is_comment_crawled IN (1, 2)"]  # 只返回已完成或正在爬取的
        params = []

        if keyword:
            where_conditions.append("keyword = %s")
            params.append(keyword)

        if status:
            if status == "crawling":
                where_conditions.append("is_comment_crawled = 2")
            elif status == "completed":
                where_conditions.append("is_comment_crawled = 1")

        where_clause = " AND ".join(where_conditions)

        # 查询总数
        count_sql = f"SELECT COUNT(*) as total FROM xhs_notes WHERE {where_clause}"
        cursor.execute(count_sql, params)
        total = cursor.fetchone()["total"]

        # 查询笔记列表
        offset = (page - 1) * page_size
        notes_sql = f"""
            SELECT
                note_id,
                title,
                author_name,
                publish_time,
                like_count,
                keyword,
                is_comment_crawled,
                create_time,
                update_time
            FROM xhs_notes
            WHERE {where_clause}
            ORDER BY update_time DESC
            LIMIT %s OFFSET %s
        """
        cursor.execute(notes_sql, params + [page_size, offset])
        notes = cursor.fetchall()

        # 处理数据格式
        for note in notes:
            note["is_comment_crawled"] = int(note["is_comment_crawled"])
            note["like_count"] = int(note["like_count"] or 0)
            # 计算评论数量（从xhs_comments表查询）
            cursor.execute(
                "SELECT COUNT(*) as count FROM xhs_comments WHERE note_id = %s",
                (note["note_id"],)
            )
            note["comment_count"] = cursor.fetchone()["count"]

        return {
            "data": notes,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            }
        }

    finally:
        cursor.close()
        conn.close()


@app.get("/xhs_craw/notes/{note_id}")
def get_note(note_id: str):
    """
    获取单个笔记详情
    """
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute("""
            SELECT
                note_id,
                note_url,
                title,
                author_name,
                author_url,
                publish_time,
                like_count,
                keyword,
                is_comment_crawled,
                create_time,
                update_time
            FROM xhs_notes
            WHERE note_id = %s AND is_comment_crawled IN (1, 2)
        """, (note_id,))

        note = cursor.fetchone()

        if not note:
            raise HTTPException(status_code=404, detail="笔记不存在")

        note["is_comment_crawled"] = int(note["is_comment_crawled"])
        note["like_count"] = int(note["like_count"] or 0)

        return note

    finally:
        cursor.close()
        conn.close()


@app.get("/xhs_craw/notes/{note_id}/comments")
def get_comments(
    note_id: str,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量")
):
    """
    获取单个笔记的评论列表
    支持分页
    """
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        # 查询总数
        cursor.execute(
            "SELECT COUNT(*) as total FROM xhs_comments WHERE note_id = %s",
            (note_id,)
        )
        total = cursor.fetchone()["total"]

        # 查询评论列表
        offset = (page - 1) * page_size
        cursor.execute("""
            SELECT
                id,
                note_id,
                comment_content,
                keyword,
                collect_time as create_time
            FROM xhs_comments
            WHERE note_id = %s
            ORDER BY collect_time ASC
            LIMIT %s OFFSET %s
        """, (note_id, page_size, offset))

        comments = cursor.fetchall()

        # 处理数据格式
        for comment in comments:
            comment["id"] = str(comment["id"])

        return {
            "data": comments,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            }
        }

    finally:
        cursor.close()
        conn.close()


@app.get("/xhs_craw/keywords")
def get_keywords():
    """
    获取所有关键词列表
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT DISTINCT keyword
            FROM xhs_notes
            WHERE keyword IS NOT NULL AND keyword != ''
            ORDER BY keyword
        """)
        keywords = [row[0] for row in cursor.fetchall()]

        return {"data": keywords}

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
