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
from comment_agent import agent_reply
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
    subprocess.Popen(cmd)
    time.sleep(3)  # 等待浏览器启动
def extract_note_id(note_url: str):
    '''
    提取node_id
    :param note_url:
    :return:
    '''
    m = re.search(r'/(?:explore|search_result)/([a-zA-Z0-9]+)', note_url)
    return m.group(1) if m else None



def single_page(page):
    '''
    # 整个页面开始单独操作
    :param page:
    :return:
    '''
    # 将鼠标移到笔记的内容上
    note_content = page.locator('.note-scroller .note-content')
    note_content.wait_for(state='visible')
    print('将鼠标移动到笔记上')
    note_content.hover()
    print('开始向下翻滚1次')
    page.wait_for_timeout(random.randint(2000, 2500))
    page.mouse.wheel(0, random.randint(1000, 1500))
    # 搞定之后按ecs退出蒙版
    print('搞定之后按ecs退出蒙版')
    page.keyboard.press('Escape')
    page.wait_for_timeout(random.randint(2000, 2500))
# 2) 入口
def crawl_content_qw(set_pause,keyword):
    '''
    :param MAX_NOTE_NUM
    :param count: 最大查找次数
    :param input_text: 旅游目的地
    :return:
    '''
    notes_data_list = []
    yumin=r'https://www.xiaohongshu.com'
    
    db_manager = DBManager()
    db_manager.connect()
    
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
        # 获取所有笔记的数量
        note_count=note_item.count()
        for i in range(note_count):
            note_i=note_item.nth(i)
            note_i.wait_for(state='visible')
            # 如果这个元素在浏览器可视区外面，让滚动到view内部
            # 这个代码无敌 很有效果
            note_i.wait_for(state='visible')
            note_i.scroll_into_view_if_needed(timeout=15000)
            # 查看笔记的id，记录到数据库里面下次防止这个笔记被访问到
            note_href=note_i.locator('a.cover.mask.ld').get_attribute('href')
            # 从笔记的href 生成笔记id
            note_id=extract_note_id(note_href)
            #bug
            # 检查该笔记是否已被访问过（有任何回复记录就跳过）
            if db_manager.check_note_replied(note_id):
                print(f'笔记 {note_id} 已被访问过，跳过')
                continue
            print(f'笔记 {note_id} 未被访问过，开始处理')
            try:
                note_i.wait_for(timeout=15000)
                # 鼠标悬停在第一个元素上方 有可能没评论
                note_i.hover(timeout=15000)
            except Exception as e:
                continue
            # 点击第一个tab
            note_i.click(delay=120)
            # 整个页面开始单独操作

            # 获取笔记标题 可能没写标题
            try:
                page.locator('#detail-title').wait_for(state='visible')
                note_title=page.locator('#detail-title').text_content(timeout=15000)
            except Exception as e:
                note_title=''


            try:
                # 获取笔记内容
                page.locator('#detail-desc').wait_for(state='visible')
                note_desc=page.locator('#detail-desc').text_content(timeout=15000)
            except Exception as e:
                note_desc=''

            # single_page(page)
            # 将鼠标移到评论区部分
            note_comment = page.locator('.comments-el')
            note_comment.wait_for(state='visible')
            note_comment.scroll_into_view_if_needed(timeout=15000)
            print('将鼠标移动到笔记上')
            note_comment.hover()
            page.wait_for_timeout(random.randint(2000, 2500))
            i=0
            while i<1:
                print(f"翻滚{i}次")
                page.mouse.wheel(0, random.randint(1500, 2000))
                page.wait_for_timeout(random.randint(2000, 2500))
                i+=1
            # 翻滚加载笔记之后 开始获取所有笔记的位置元素
            no_comments_flag=page.locator('.no-comments').is_visible()
            # 没评论的部分
            if no_comments_flag is True:
                # 搞定之后按ecs退出蒙版
                print('没评论按ecs退出蒙版')
                page.keyboard.press('Escape')
                page.wait_for_timeout(random.randint(2000, 2500))
                continue
            parent_comment=page.locator('.comments-container .list-container .parent-comment')
            if parent_comment.first.is_visible(timeout=15000) is False:
                # 搞定之后按ecs退出蒙版
                print('没评论按ecs退出蒙版')
                page.keyboard.press('Escape')
                page.wait_for_timeout(random.randint(2000, 2500))
                continue
            parent_comment.first.wait_for(state='visible')
            parent_comment_count=parent_comment.count()
            
            # 根据评论数量动态设置最大回复数：评论少于5条只回复1条，评论>=5条最多回复5条
            max_reply_count = 1 if parent_comment_count < 5 else 5
            print(f'该笔记共有{parent_comment_count}条评论，最多回复{max_reply_count}条')
            
            # 本次访问该笔记已回复的数量
            current_note_replied = 0
            # 当前遍历的评论索引
            comment_index = 0

            while comment_index < parent_comment_count and current_note_replied < max_reply_count:
                # 定位到一个评论区的下方
                p_comment=parent_comment.nth(comment_index)
                if p_comment.is_visible(timeout=15000):
                    # 页面滑动到这个位置
                    page.wait_for_timeout(random.randint(3000,5000))
                    p_comment.scroll_into_view_if_needed(timeout=15000)
                    # 获取这个用户下面的首评
                    comment_first=p_comment.locator('.comment-item>.comment-inner-container>.right ').first
                    # 获取评论内容
                    comment_content_list=comment_first.all_text_contents()
                    comment_content=' '.join(comment_content_list)
                    print('agent 开始思考')
                    agent_res=agent_reply(note_title,note_desc,comment_content)
                    print(f'发送给agent的内容:{comment_content}')
                    print(f'agent 思考完成\n 回答内容:{agent_res}')

                    # 将AI回复记录存入数据库
                    record_data = {
                        'note_id': note_id,
                        'note_title': note_title,
                        'note_desc': note_desc,
                        'comment_content': comment_content,
                        'reply_text': agent_res.reply_text if agent_res.reply_text else '',
                        'is_like': 1 if agent_res.like else 0,
                        'reply_bool': 1 if agent_res.reply_bool else 0,
                        'reason_text': agent_res.reason_text if agent_res.reason_text else '',
                        'keyword': keyword
                    }
                    # 对这个评论进行关注
                    if agent_res.like:
                        like=comment_first.locator('.info .interactions .like span.like-lottie')
                        # like.hover(timeout=15000)
                        like.click(delay=53,timeout=15000)
                        page.wait_for_timeout(timeout=random.randint(1500,3000))
                        print('电赞结束')
                    # 接下来对这个评论进行回复
                    # 获取到评论的位置
                    # AI 判断是否值得回复
                    if agent_res.reply_bool:
                        try:
                            reply=comment_first.locator('.info .interactions .reply.icon-container')
                            reply.wait_for(state='visible')
                            reply.hover(timeout=10500)
                            reply.click(timeout=100)
                            page.wait_for_timeout(timeout=random.randint(1500, 3000))
                            # 这时候出现评论框
                            content_textarea=page.locator('#content-textarea')
                            # 如果这个出现了 就输出文本
                            if content_textarea.is_visible():
                                content_textarea.type(agent_res.reply_text,delay=100)
                                page.wait_for_timeout(timeout=1500)
                                # 回车发送消息
                                page.keyboard.press("Enter")
                                page.wait_for_timeout(timeout=1500)
                                page.wait_for_timeout(random.randint(5000,7000))

                            print('入库数据')
                            print(record_data)
                            db_manager.insert_agent_record(record_data)
                            print(f'已将AI回复记录存入数据库')

                            # 标记本次已回复1条
                            current_note_replied += 1
                            # 随机跳过1-2个评论，避免连续评论
                            skip_count = random.randint(1, 2)
                            comment_index += skip_count
                            print(f'已回复1条，跳过{skip_count}个评论')
                        except Exception as e:
                            print('评论操作失败，未知原因，跳过该次操作')
                    else:
                        # 如果没有实际回复，继续下一个评论
                        comment_index += 1
                else:
                    # 评论不可见，继续下一个
                    comment_index += 1

            # 搞定之后按ecs退出蒙版
            print('搞定之后按ecs退出蒙版')
            page.keyboard.press('Escape')
            page.wait_for_timeout(random.randint(2000, 2500))

            if i>0:
                pass
                # break
        print('退出搜索')
    
    db_manager.close()
    return notes_data_list

if __name__=="__main__":
    keyword = '创业'
    notes_list=crawl_content_qw(set_pause=False,keyword=keyword)
    print(f'共爬取{len(notes_list)}条笔记')

