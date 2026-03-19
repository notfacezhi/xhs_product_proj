import imaplib
import email
from email.header import decode_header

# --- 配置区域 ---
GMAIL_USER = 'zhihu7056@gmail.com'
GMAIL_PASS = 'plqkgckehaqpagud'  # 16位应用专用密码


# ----------------

def connect_gmail():
    try:
        # 1. 连接到 Gmail 的 IMAP 服务器 (使用 SSL 端口 993)
        print("正在连接服务器...")
        mail = imaplib.IMAP4_SSL("imap.gmail.com")

        # 2. 登录
        mail.login(GMAIL_USER, GMAIL_PASS)
        print("登录成功！")

        # 3. 选择收件箱 (INBOX)
        # readonly=True 表示只读，不会把邮件标记为已读
        mail.select("INBOX", readonly=True)

        # 4. 搜索邮件 (搜索所有邮件 'ALL')
        # 返回的 data 是一个列表，包含了匹配邮件的 ID
        status, data = mail.search(None, 'ALL')

        # 获取所有邮件 ID 列表
        mail_ids = data[0].split()
        print(f"收件箱共有 {len(mail_ids)} 封邮件。")

        # 5. 读取最近的一封邮件 (最后一封)
        if mail_ids:
            latest_email_id = mail_ids[-1]
            # 获取邮件内容 (RFC822 格式)
            status, data = mail.fetch(latest_email_id, '(RFC822)')

            raw_email = data[0][1]
            # 将字节流转换为邮件对象
            msg = email.message_from_bytes(raw_email)

            # 6. 解析邮件主题
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else 'utf-8')

            print(f"\n最新邮件主题: {subject}")
            print(f"发件人: {msg.get('From')}")
            print(f"日期: {msg.get('Date')}")

        # 7. 登出
        mail.logout()

    except Exception as e:
        print(f"发生错误: {e}")


if __name__ == "__main__":
    connect_gmail()