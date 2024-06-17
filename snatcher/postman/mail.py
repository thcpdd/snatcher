"""
The wrapper of send email.
    The detail calling to see: if __name__ == '__main__'
"""
import smtplib
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.header import Header

from jinja2 import Template

from snatcher.conf import settings


def include_chinese(string: str):
    """Judging current string is including Chinese or not."""
    for char in string:
        if u'\u4e00' <= char <= u'\u9fff':
            return True
    return False


class EmailSender:
    def __init__(self, receiver_email, subject, content):
        email_config = settings.EMAIL_CONFIG
        self.email_from = email_config['email_from']
        self.sender_name = email_config['name']
        self.receiver_email = receiver_email
        self.subject = subject
        self.content = content
        self.smtp = smtplib.SMTP_SSL(email_config['host'])
        self.smtp.connect(email_config['host'], port=email_config['port'])
        self.smtp.login(user=self.email_from, password=email_config['verify_code'])

    def send(self):
        """send email"""
        html_content = MIMEText(self.content, 'html', 'utf-8')
        message = MIMEMultipart('related')
        message['From'] = Header(self.get_sender_name())
        message['To'] = Header(self.receiver_email, 'utf-8')
        message['Subject'] = Header(self.subject)

        with open('./files/snatcher-low-quality.png', 'rb') as f:
            image = MIMEImage(f.read())
            image.add_header('Content-ID', '<snatcher>')

        message.attach(html_content)
        message.attach(image)

        self.smtp.sendmail(from_addr=self.email_from, to_addrs=self.receiver_email, msg=message.as_string())
        self.smtp.quit()  # quit session with smtp server

    def get_sender_name(self):
        """
        struct sender name.
        detail: https://service.mail.qq.com/detail/124/995
        """
        name = self.sender_name
        if include_chinese(name):
            name = base64.b64encode(name.encode('utf-8')).decode('utf-8')
            return f'=?utf-8?B?{name}?= <{self.email_from}>'
        return f'{name} <{self.email_from}>'


def get_success_content(username: str, course_name: str) -> str:
    """Reading and rendering the HTML mail content."""
    with open('./files/mail.html', encoding='utf8') as f:
        html_file = f.read()
        template = Template(html_file)
        return template.render(username=username, course_name=course_name)


def send_email(
    receiver_email: str,
    username: str,
    course_name: str,
    success: bool = True,
    failed_reason: str = None
):
    if success:
        subject = '恭喜你，选课成功！!'
        content = get_success_content(username, course_name)
    else:
        subject = '选课失败通知'
        content = "学号为 %s 的意向课程 <%s> 选课失败，原因：%s" % (username, course_name, failed_reason)

    try:
        EmailSender(receiver_email, subject, content).send()
    except Exception as exception:
        return 0, str(exception)
    return 1, ''


if __name__ == '__main__':
    send_email('1834763300@qq.com', '2204425143', '人工智能应用零基础入门与零代码实战+无人驾驶实训营', True)
