"""
发送邮件
"""
import smtplib
import base64
from email.mime.text import MIMEText
from email.header import Header

from snatcher.conf import settings


def include_chinese(string):
    """判断用户名是否包含中文"""
    for content in string:
        if u'\u4e00' <= content <= u'\u9fff':
            return True
    return False


class SendEmail:
    def __init__(self, receiver_email, subject, content):
        email_config = settings.EMAIL_CONFIG
        self.email_from = email_config['email_from']
        self.sender_name = email_config['name']
        self.receiver_email = receiver_email
        self.subject = subject
        self.content = content
        self.smtp = smtplib.SMTP()
        self.smtp.connect(email_config['host'], port=email_config['port'])  # 465/587为QQ邮箱的smtp端口号
        self.smtp.login(user=self.email_from, password=email_config['verify_code'])

    def send(self):
        """发送邮件"""
        message = MIMEText(self.content, 'plain', 'utf-8')
        message['From'] = Header(self.get_sender_name(self.sender_name))
        message['To'] = Header(self.receiver_email, 'utf-8')
        message['Subject'] = Header(self.subject)
        self.smtp.sendmail(from_addr=self.email_from, to_addrs=self.receiver_email, msg=message.as_string())
        self.smtp.close()  # 与服务器断开连接

    def get_sender_name(self, name):
        """
        构造发件人昵称
        详见：https://service.mail.qq.com/detail/124/995
        """
        if include_chinese(name):
            name = base64.b64encode(name.encode('utf-8')).decode('utf-8')
        return f'=?utf-8?B?{name}?= <{self.email_from}>'


def send_email(receiver_email: str, subject: str, content: str):
    SendEmail(receiver_email, subject, content).send()


if __name__ == '__main__':
    send_email('1834763300@qq.com', '选课结果通知', '学号为%s的同学：\n你好，您选择的课程《%s》已经选课成功，感谢您对我们的信任，谢谢！' % ('2204425143', '毽球'))
