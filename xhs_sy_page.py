'''
# 爬取小红书网站
'''
import random
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
import os
import re
from tqdm import tqdm
import subprocess
import psutil

from db_manager import DBManager

profile_dir = Path(r"D:\application\mfw_tmp_test")  # ← 改成你的路径
# profile_dir = Path(r"/home/ecs-assist-user/hz/mfw_tmp")  # ← 改成你的路径
# profile_dir.mkdir(parents=True, exist_ok=True)
headless_set = True # true是无头模式 false是有头模式
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

def extract_note_id(note_url: str):
    '''
    提取node_id
    :param note_url:
    :return:
    '''
    m = re.search(r'/(?:explore|search_result)/([a-zA-Z0-9]+)', note_url)
    return m.group(1) if m else None


# 2) 入口
def crawl_content_qw(set_pause,MAX_NOTE_NUM=50,count=10,keyword=''):
    '''
    :param MAX_NOTE_NUM
    :param count: 最大查找次数
    :param input_text: 旅游目的地
    :return:
    '''
    notes_data_list = []
    yumin=r'https://www.xiaohongshu.com'
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

        try:
            page.goto(f"https://www.xiaohongshu.com/search_result?keyword={keyword }&type=51", wait_until="load", timeout=10000)
        except Exception as e:
            print(e)
            page.reload(timeout=100000)
        if set_pause:
            page.pause()
        page.locator('.feeds-container').wait_for(state='visible')
        # 加载小红书多个笔记
        note_item=page.locator('.feeds-container > .note-item')
        # 鼠标悬停在第一个元素上方
        note_item.first.hover()

        # 记录连续多少次去重后数量不变
        unchanged_count = 0
        prev_notes_count = 0
        for j in range(count):
            # 加载小红书多个笔记
            note_item = page.locator('.feeds-container > .note-item')
            note_count=note_item.count()
            print(f'检测到的笔记数量:{note_count}')
            for i in tqdm(range(note_count)):
                try:
                    # 获取笔记的主页地址
                    note_href_str=note_item.nth(i).locator('a.cover.mask.ld').get_attribute('href',timeout=1500)
                    note_id=extract_note_id(note_href_str)
                    note_href_str = f'{yumin}{note_href_str}'
                    footer=note_item.nth(i).locator('div.footer')
                    # 获取笔记的标题信息
                    title=footer.locator('.title>span').text_content(timeout=1500)
                    # 获取作者主页地址
                    author_href=footer.locator('.author').get_attribute('href')
                    author_href = f'{yumin}{author_href}'
                    # 获取作者的name
                    name=footer.locator('.author .name-time-wrapper .name').text_content(timeout=1500)
                    # 获取时间
                    time=footer.locator('.author .name-time-wrapper .time').text_content(timeout=1500)

                    # 点赞的数量
                    like=footer.locator('.card-bottom-wrapper .like-wrapper.like-active .count').text_content(timeout=1500)

                    print(f'name:{name},time:{time},like:{like},author_href:{author_href},note_href_str:{note_href_str}')

                    note_data = {
                        'note_id':note_id,
                        'note_url': note_href_str,
                        'title': title,
                        'author_name': name,
                        'author_url': author_href,
                        'publish_time': time,
                        'like_count': like,
                        'keyword': keyword
                    }
                    notes_data_list.append(note_data)

                except Exception as e:
                    # e.with_traceback()
                    print(f'{i}笔记出问题没信息')
            # 去重根据note_id
            notes_data_list = list(
                {item["note_id"]: item for item in notes_data_list}.values()
            )
            
            current_notes_count = len(notes_data_list)
            if current_notes_count == prev_notes_count:
                unchanged_count += 1
                print(f'去重后数量未变化，连续{unchanged_count}次')
            else:
                unchanged_count = 0
            prev_notes_count = current_notes_count
            
            if unchanged_count >= 4:
                print(f'连续4次去重后数量不变，提前结束爬取')
                break
            
            if len(notes_data_list) >MAX_NOTE_NUM:
                notes_data_list=notes_data_list[:MAX_NOTE_NUM]
                break
            print(f'下拉{j}次')
            page.mouse.wheel(0, random.randint(1500, 2000))
            page.wait_for_timeout(random.randint(100, 200))
        print('退出搜索')
    db_manager = DBManager()
    db_manager.connect()

    # 1. 先检查哪些笔记已存在
    all_note_ids = [note['note_id'] for note in notes_data_list]
    existing_note_ids = db_manager.check_notes_exist(all_note_ids)
    print(f"已存在 {len(existing_note_ids)} 个笔记")

    # 2. 过滤掉已存在的，只保留新的
    new_notes_list = [note for note in notes_data_list if note['note_id'] not in existing_note_ids]
    print(f"准备插入 {len(new_notes_list)} 个新笔记")

    # 3. 插入新的笔记
    if new_notes_list:
        db_manager.batch_insert_notes(new_notes_list)
        print(f'成功存入{len(new_notes_list)}条新笔记数据到数据库')
    else:
        print('没有需要插入的新笔记')

    db_manager.close()

    return notes_data_list

if __name__=="__main__":
    # 示例：如何使用无头模式切换

    # 方式1：默认使用有头模式
    print("=== 默认有头模式 ===")
    keyword = '创业心得'
    notes_list=crawl_content_qw(set_pause=False,MAX_NOTE_NUM=50,keyword=keyword)
    print(f'共爬取{len(notes_list)}条笔记')

'''

https://www.xiaohongshu.com/search_result?keyword=旅游规划app推荐&type=51

'''