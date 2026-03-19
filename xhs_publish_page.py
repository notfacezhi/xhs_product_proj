'''
# 小红书自动发布
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


# 2) 入口
def crawl_content_qw(set_pause,photo_content,title_text,content_text,tag_list):
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
            page.goto(f"https://creator.xiaohongshu.com/publish/publish?from=menu&target=image", wait_until="load", timeout=10000)
        except Exception as e:
            print(e)
            page.reload(timeout=100000)
        if set_pause:
            page.pause()


        # 配图界面
        text2image_button=page.locator('.el-button.upload-button.text2image-button')
        text2image_button.wait_for(state='visible')
        text2image_button.click(timeout=15000,delay=120)
        ProseMirror=page.locator('.tiptap.ProseMirror')
        ProseMirror.wait_for(state='visible')
        ProseMirror.type(photo_content,delay=130)

        print('开始点击生图按钮')
        # page.pause()
        # 点击编辑按钮生成图片
        page.wait_for_timeout(random.randint(2000,3000))
        edit_button=page.locator('div.edit-text-button')
        edit_button.wait_for(state='visible')
        edit_button.hover(timeout=15000)
        edit_button.click(timeout=15000,delay=120)

        # 进入到选择卡片页面
        item_container=page.locator('.cover-item-container')
        item_container.first.wait_for(state='visible',timeout=15000)
        assert item_container.count()>0,'有问题'
        # 鼠标选择第一个卡片
        item_container.nth(0).click(timeout=15000)
        page.wait_for_timeout(random.randint(1500,2000))
        # 下一步按钮
        next_step=page.locator('.d-button-content')
        next_step.click(timeout=15000)

        # 到发布页面
        title=page.locator('.plugin.title-container')
        title.wait_for(state='visible',timeout=15000)
        title_input=title.locator('.d-input-wrapper.d-inline-block.c-input_inner')
        title_input.click(timeout=15000,delay=80)
        # 输入标题

        title_input.type(title_text,delay=120,timeout=15000)

        # 输入正文
        content_input=page.locator('.plugin.editor-container .editor-content')


        content_input.click(timeout=15000,delay=80)
        # 全选
        page.keyboard.press("Control+A")
        page.wait_for_timeout(1500)
        # 清空
        page.keyboard.press("Backspace")
        page.wait_for_timeout(1500)
        content_input.type(content_text,delay=120,timeout=60000)

        # 给文章尾部加上标签
        # 加标签就得讲究
        # 先来个回车单独一行
        page.keyboard.press('Enter')
        for tag in tag_list:
            # 开始加标签
            content_input.type(f"#{tag}",delay=120,timeout=15000)
            page.wait_for_timeout(1500)
            page.keyboard.press('Enter')

        page.wait_for_timeout(1500)
        # 移动到提交按钮上
        submit_btn=page.locator('div.submit .submit .d-button-content').first
        submit_btn.wait_for(state='visible')
        # submit_btn.click(timeout=15000,delay=80)

    return notes_data_list

if __name__=="__main__":
    # 笔记配置页面
    # ---------------------
    photo_content = "创业就玩两件事 \n1.第一件事不是产品，是人群"
    title_text = '一个03年男孩给我上了一课'
    content_text = '''\n他零成本当滑雪教练中间商\n
    靠小红书引流获客,\n
    让技术一流却缺客户的教练授课,\n
    教练时薪收400元，他向客户收600元,\n
    教练辛苦授课，他躺赚差价，单雪季就赚了几十万。\n
    这揭示了产品过剩时代的商机：研究流量比产品更重要。\n
    如今小红书0粉丝可挂车卖货，\n
    选爆品发内容，出单后让商家发货，自己赚差价即可。\n
    2026年，没背景资源的人要走野路子，\n
    聚焦流量、新事物与稀缺资源，\n
    以一人公司模式撬动百万利润，\n
    牢记人属于市场而非某家公司，认知决定收入上限。'''
    # 专门打tag标签
    tag_list = ["创业", "机遇", "流量"]
    # --------------------
    notes_list=crawl_content_qw(set_pause=False,photo_content=photo_content,
        title_text=title_text,content_text=content_text,tag_list=tag_list)


