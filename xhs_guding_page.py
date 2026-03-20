'''
小红书固定页面测试
'''
'''
# 爬取小红书网站
'''
import random
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
import os
import subprocess
import psutil
import json
import re

from db_manager import DBManager
profile_dir = Path(r"D:\application\mfw_tmp_test")  # ← 改成你的路径
# profile_dir = Path(r"/home/ecs-assist-user/hz/mfw_tmp")  # ← 改成你的路径
# profile_dir.mkdir(parents=True, exist_ok=True)
headless_set = False # true是无头模式 false是有头模式
DEBUG_PORT = 9222  # 远程调试端口
print("无头模式" if headless_set else "有头模式")

def is_browser_running(port=9222):
    """检查指定端口的浏览器是否在运行"""
    for conn in psutil.net_connections():
        if conn.laddr.port == port and conn.status == 'LISTEN':
            return True
    return False

def launch_browser_with_debug(port=9222):
    """以调试模式启动Chrome浏览器"""
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"  # 根据实际路径调整
    cmd = [
        chrome_path,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={profile_dir}",
    ]

    # 根据模式添加无头参数
    if headless_set:
        cmd.extend([
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
        ])
        start_delay = 5  # 无头模式需要更长时间
    else:
        start_delay = 3  # 有头模式正常时间

    subprocess.Popen(cmd)
    time.sleep(start_delay)  # 等待浏览器启动


def set_headless_mode(headless=True):
    """
    设置无头/有头模式
    :param headless: True为无头模式，False为有头模式
    """
    global headless_set
    headless_set = headless
    print(f"已切换为{'无头模式' if headless_set else '有头模式'}")


def toggle_headless_mode():
    """
    切换无头/有头模式
    """
    global headless_set
    headless_set = not headless_set
    print(f"已切换为{'无头模式' if headless_set else '有头模式'}")
    print("下次启动浏览器时将使用新模式")

# 2) 入口
def dump_scroll_state(page):
    return page.evaluate("""
    () => {
      const se = document.scrollingElement;
      const comment = document.querySelector('.comments-container .list-container');
      return {
        pageScrollTop: se ? se.scrollTop : null,
        pageScrollHeight: se ? se.scrollHeight : null,
        pageClientHeight: se ? se.clientHeight : null,
        commentScrollTop: comment ? comment.scrollTop : null,
        commentScrollHeight: comment ? comment.scrollHeight : null,
        commentClientHeight: comment ? comment.clientHeight : null,
      };
    }
    """)

def crawl_single_note_comments(page, note_id, note_url, set_pause=False):
    '''
    在已有页面上爬取单个笔记的评论
    :param page: Playwright页面对象
    :param note_id: 笔记ID
    :param note_url: 笔记URL
    :param set_pause: 是否暂停调试
    :return: 评论列表
    '''
    comment_text_list = []
    try:
        page.goto(note_url, wait_until="load", timeout=10000)
    except Exception as e:
        print(f'[{note_id}] 页面加载失败: {e}')
        page.reload(timeout=100000)
    
    if set_pause:
        page.pause()
    
    page.locator('#detail-desc').hover()
    MAX_COMMENT_LIMIT = 100
    MAX_SAME_TIMES = 3

    last_count = 0
    same_count_times = 0

    # ------ 加载信息 爬取笔记信息------
    # 等待页面加载完成
    page.wait_for_timeout(2000)

    # 获取 window.__INITIAL_STATE__
    initial_state = page.evaluate("""
        () => {
            if (window.__INITIAL_STATE__ &&
                window.__INITIAL_STATE__.note &&
                window.__INITIAL_STATE__.note.noteDetailMap) {
                const noteDetailMap = window.__INITIAL_STATE__.note.noteDetailMap;
                return JSON.stringify(noteDetailMap);
            }
            return "";
        }
    """)
    note_content = None
    if initial_state:
        note_detail_map = json.loads(initial_state)
        if note_id in note_detail_map:
            note_detail = note_detail_map[note_id]
            note_data = note_detail.get('note', {})
            note_content = {
                'note_id': note_id,
                'desc': note_data.get('desc', ''),
                'type': note_data.get('type', ''),
                'image_list': [img.get('urlDefault', img.get('url', ''))
                               for img in note_data.get('imageList', [])],
                'video_url': None,
                'tags': [tag.get('name', '') for tag in note_data.get('tagList', []) if tag.get('name')],
                'topic': note_data.get('topic', {}).get('name', '') if note_data.get('topic') else '',
                'ip_location': note_data.get('ipLocation', ''),
                'collected_count': note_data.get('interactInfo', {}).get('collectedCount', 0),
                'share_count': note_data.get('interactInfo', {}).get('shareCount', 0),
                'comment_count': note_data.get('interactInfo', {}).get('commentCount', 0),
            }
            print("笔记信息----")
            print(note_content)

            # 视频信息
            if note_data.get('video'):
                video = note_data['video']
                if video.get('media') and video['media'].get('stream'):
                    h264_list = video['media']['stream'].get('h264', [])
                    if h264_list:
                        note_content['video_url'] = h264_list[0].get('masterUrl', '')

            print(f"[{note_id}] 笔记信息获取成功:")
            print(f"  - 类型: {note_content['type']}")
            print(f"  - 描述长度: {len(note_content['desc'])}")
            print(f"  - 图片数: {len(note_content['image_list'])}")
            print(f"  - 视频URL: {'有' if note_content['video_url'] else '无'}")
            print(f"  - 标签: {note_content['tags']}")

            # 更新笔记内容到数据库
            try:
                db = DBManager()
                db.connect()
                db.update_note_content(note_content)
                db.close()
            except Exception as e:
                print(f"[{note_id}] 更新笔记内容到数据库失败: {e}")
        else:
            print(f"[{note_id}] 未在 noteDetailMap 中找到")
    else:
        print(f"[{note_id}] 未获取到 __INITIAL_STATE__")

    print(f"[{note_id}] 开始滚动加载评论（最多 {MAX_COMMENT_LIMIT} 条）...")

    while True:
        comment_list = page.locator(
            '.comments-container > .list-container > .parent-comment'
        )
        current_count = comment_list.count()

        print(f"[{note_id}] 当前评论数: {current_count}")

        if current_count >= MAX_COMMENT_LIMIT:
            print(f"[{note_id}] 已达到最大评论数限制: {MAX_COMMENT_LIMIT}")
            break

        if current_count == last_count:
            same_count_times += 1
            if same_count_times >= MAX_SAME_TIMES:
                print(f"[{note_id}] 评论数量不再增长，已到底")
                break
        else:
            same_count_times = 0
            last_count = current_count

        scroll_distance = random.randint(800, 3000)
        if random.random() < 0.05:
            scroll_distance = -random.randint(200, 500)
        
        page.mouse.wheel(0, scroll_distance)
        page.wait_for_timeout(random.randint(10000, 30000))

    comment_list = page.locator('.comments-container > .list-container > .parent-comment')
    comment_count = comment_list.count()
    print(f'[{note_id}] 总数量:{comment_count}')

    for i in range(comment_count):
        comment_obj = comment_list.nth(i)
        comment_obj1 = comment_obj.locator('.comment-item>.comment-inner-container>.right').first.locator('.note-text')
        comment_text = comment_obj1.text_content()
        comment_text_list.append(comment_text)
    
    return comment_text_list


def crawl_content_qw(set_pause, note_id, note_url):
    '''
    单个笔记爬取（保持原有接口兼容性）
    :param set_pause: 是否暂停调试
    :param note_id: 笔记ID
    :param note_url: 笔记URL
    :return:
    '''
    # 标记笔记为正在爬取
    db_manager = DBManager()
    db_manager.connect()
    db_manager.mark_note_as_crawling(note_id)
    db_manager.close()

    # 检查浏览器是否已运行，未运行则启动
    if not is_browser_running(DEBUG_PORT):
        print(f"浏览器未运行，正在启动并监听端口 {DEBUG_PORT}...")
        launch_browser_with_debug(DEBUG_PORT)
    else:
        print(f"检测到浏览器已在端口 {DEBUG_PORT} 运行，直接连接...")
    
    with sync_playwright() as p:
        # 连接到已存在的浏览器实例
        browser = p.chromium.connect_over_cdp(f"http://localhost:{DEBUG_PORT}")
        context = browser.contexts[0] if browser.contexts else browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale="zh-CN,zh;q=0.9",
            timezone_id="Asia/Shanghai",
        )
        # 复用已存在的标签页，如果没有则创建新的
        if context.pages:
            page = context.pages[0]  # 使用第一个已存在的标签页
            print(f"复用已存在的标签页，当前共有 {len(context.pages)} 个标签页")
        else:
            page = context.new_page()
            print("创建新标签页")
        comment_text_list = crawl_single_note_comments(page, note_id, note_url, set_pause)
        wait_ms = random.randint(3000, 6000)
        page.wait_for_timeout(wait_ms)
        page.close()
    
    db_manager = DBManager()
    db_manager.connect()
    db_manager.batch_insert_comments(note_id, note_url, comment_text_list)
    # 标记笔记为已爬取
    db_manager.mark_note_as_crawled(note_id)
    db_manager.close()
    print(f'成功存入{len(comment_text_list)}条评论数据到数据库，并标记为已爬取')

    return comment_text_list


def crawl_multiple_notes_from_db(max_concurrent=2, limit=None, date_filter=None, keyword=None):
    '''
    从数据库读取笔记并使用多标签页并行爬取评论
    :param max_concurrent: 最多同时打开几个标签页
    :param limit: 限制爬取的笔记数量，None表示全部
    :param date_filter: 日期筛选，格式：'2026-01-06' 或 None（不筛选）
    :param keyword: 关键词筛选，筛选指定关键词的笔记，None表示不筛选
    :return: 成功爬取的笔记数量
    '''
    db_manager = DBManager()
    db_manager.connect()
    
    sql = """
    SELECT note_id, note_url, keyword
    FROM xhs_notes
    WHERE is_comment_crawled = 0
    """
    
    if date_filter:
        sql += f" AND DATE(create_time) = '{date_filter}'"
    
    if keyword:
        sql += f" AND keyword = '{keyword}'"
    
    sql += " ORDER BY CAST(like_count AS UNSIGNED) DESC"
    
    if limit:
        sql += f" LIMIT {limit}"
    
    db_manager.cursor.execute(sql)
    notes_list = db_manager.cursor.fetchall()
    db_manager.close()
    
    if not notes_list:
        print("数据库中没有笔记数据")
        return 0
    
    print(f"从数据库读取到 {len(notes_list)} 条笔记")
    
    success_count = 0
    
    # 检查浏览器是否已运行，未运行则启动
    if not is_browser_running(DEBUG_PORT):
        print(f"浏览器未运行，正在启动并监听端口 {DEBUG_PORT}...")
        launch_browser_with_debug(DEBUG_PORT)
    else:
        print(f"检测到浏览器已在端口 {DEBUG_PORT} 运行，直接连接...")
    
    with sync_playwright() as p:
        # 连接到已存在的浏览器实例
        browser = p.chromium.connect_over_cdp(f"http://localhost:{DEBUG_PORT}")
        context = browser.contexts[0] if browser.contexts else browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale="zh-CN,zh;q=0.9",
            timezone_id="Asia/Shanghai",
        )
        
        for i, (note_id, note_url, note_keyword) in enumerate(notes_list):
            try:
                print(f"\n[{i+1}/{len(notes_list)}] 开始爬取笔记: {note_id} (关键词: {note_keyword})")

                # 标记笔记为正在爬取
                db_manager = DBManager()
                db_manager.connect()
                db_manager.mark_note_as_crawling(note_id)
                db_manager.close()
                
                page = context.new_page()
                # page.pause()
                comment_list = crawl_single_note_comments(page, note_id, note_url)
                
                db_manager = DBManager()
                db_manager.connect()
                db_manager.batch_insert_comments(note_id, note_url, comment_list, note_keyword)
                # 标记笔记为已爬取
                db_manager.mark_note_as_crawled(note_id)
                db_manager.close()

                print(f"[{note_id}] 成功存入 {len(comment_list)} 条评论到数据库，并标记为已爬取")
                success_count += 1
                
            except Exception as e:
                print(f"[{note_id}] 爬取失败: {e}")
            
            finally:
                page.close()
                print(f"[{note_id}] 关闭标签页")
                
                if i < len(notes_list) - 1:
                    print(f"等待 5 秒后继续下一个笔记...")
                    time.sleep(5)
        
        print('爬取任务完成')
    
    print(f"\n爬取完成！成功: {success_count}/{len(notes_list)}")
    return success_count


if __name__=="__main__":
    # 示例：如何使用无头模式切换

    # 方式1：默认使用有头模式（headless_set = False）
    print("=== 默认有头模式 ===")
    # 单个笔记爬取
    test_note_id = "6709f2de000000002401a2a9"
    test_note_url = "https://www.xiaohongshu.com/search_result/6709f2de000000002401a2a9?xsec_token=AB5fMSn8DRaR909wMGdRM58DbZaWQ4MUK6I4cm951pnEY=&xsec_source="
    comment_text_list = crawl_content_qw(set_pause=False, note_id=test_note_id, note_url=test_note_url)

    # 方式2：切换到无头模式
    # print("\n=== 切换到无头模式 ===")
    # set_headless_mode(True)  # 设置为无头模式

    # 方式3：在无头/有头之间切换
    # toggle_headless_mode()  # 在无头/有头之间切换

    # 方式4：批量爬取笔记（使用当前设置的模式）
    # print("\n=== 批量爬取（无头模式） ===")
    # 爬取所有笔记中点赞数最高的前10条
    # crawl_multiple_notes_from_db(max_concurrent=2, limit=10)

    # 爬取1月6号的笔记中点赞数最高的前10条
    # crawl_multiple_notes_from_db(max_concurrent=1, limit=2, date_filter='2026-03-19')

    # 爬取关键词为"旅游规划app推荐"的笔记中点赞数最高的前10条
    # crawl_multiple_notes_from_db(max_concurrent=2, limit=10, keyword='旅游规划app推荐')

    # 组合筛选：爬取1月6号、关键词为"旅游规划app推荐"的笔记中点赞数最高的前5条
    # crawl_multiple_notes_from_db(max_concurrent=2, limit=10, date_filter='2026-01-09', keyword='ai使用心得')



