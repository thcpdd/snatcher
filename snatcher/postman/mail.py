"""
The wrapper of send email.
    The detail calling to see: if __name__ == '__main__'
"""
import hmac
import hashlib
import time
import json
import ssl
import smtplib
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.message import Message
from http.client import HTTPSConnection
from datetime import datetime

from jinja2 import Template

from snatcher.conf import settings
from snatcher.storage.mongo import get_security_key


def include_chinese(string: str):
    """Judging current string is including Chinese or not."""
    for char in string:
        if u'\u4e00' <= char <= u'\u9fff':
            return True
    return False


class EmailConfiguration:
    def __init__(self):
        config = settings.EMAIL_CONFIG
        self.sender = config.get('sender')
        self.password = config.get('password')
        self.host = config.get('host')
        self.port = config.get('port')

        # struct sender name.
        # detail: https://service.mail.qq.com/detail/124/995
        name = config.get('name')
        if include_chinese(name):
            name = base64.b64encode(name.encode('utf-8')).decode('utf-8')
            self.name = f'=?utf-8?B?{name}?= <{self.sender}>'
        else:
            self.name = f'{name} <{self.sender}>'


class AbstractEmailSender:
    def send(self):
        raise NotImplementedError


class SMTPEmailSender(AbstractEmailSender):
    def __init__(self, *, receiver: str, subject: str, content: str = None, **_):
        self.config = EmailConfiguration()
        self.subject = subject
        self.content = content
        self.receiver = receiver

    def get_message(self) -> Message:
        raise NotImplementedError

    def send(self):
        host = self.config.host
        port = self.config.port
        user = self.config.sender
        password = self.config.password
        context = ssl.create_default_context()
        context.set_ciphers('DEFAULT')

        smtp = smtplib.SMTP_SSL(host, context=context)
        smtp.connect(host, port=port)
        smtp.login(user=user, password=password)

        message: Message = self.get_message()
        message['From'] = Header(self.config.name)
        message['To'] = Header(self.receiver, 'utf-8')
        message['Subject'] = Header(self.subject)

        smtp.sendmail(from_addr=user, to_addrs=self.receiver, msg=message.as_string())
        smtp.quit()


class HTMLEmailSender(SMTPEmailSender):
    def get_message(self):
        html_content = MIMEText(self.content, 'html', 'utf-8')
        message = MIMEMultipart('related')
        message.attach(html_content)
        return message


class TextEmailSender(SMTPEmailSender):
    def get_message(self):
        return MIMEText(self.content, 'plain', 'utf-8')


class TencentCloudEmailSender(AbstractEmailSender):
    def __init__(self, *, receiver: str, subject: str, username: str, course_name: str, **_):
        self.receiver = receiver
        self.subject = subject
        self.username = username
        self.service = "ses"
        self.host = "ses.tencentcloudapi.com"
        self.algorithm = "TC3-HMAC-SHA256"
        self.action = 'SendEmail'
        self.secret_key = get_security_key('tencent_cloud_secret_key')
        self.secret_id = get_security_key('tencent_cloud_secret_id')
        payload = {
            'FromEmailAddress': '智能抢课系统-邮箱小助手 <snatcher@thcpdd.com>',
            'Destination': [receiver],
            'Subject': subject,
            'Template': {
                'TemplateID': 29502,
                "TemplateData": json.dumps({'username': username, 'course_name': course_name})
            }
        }
        self.payload = json.dumps(payload)

    @classmethod
    def _sign(cls, key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    def _get_authorization(self):
        service = "ses"
        timestamp = int(time.time())
        date = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")

        # ************* 步骤 1：拼接规范请求串 *************
        http_request_method = "POST"
        canonical_uri = "/"
        canonical_querystring = ""
        ct = "application/json; charset=utf-8"
        canonical_headers = "content-type:%s\nhost:%s\nx-tc-action:%s\n" % (ct, self.host, self.action.lower())
        signed_headers = "content-type;host;x-tc-action"
        hashed_request_payload = hashlib.sha256(self.payload.encode("utf-8")).hexdigest()
        canonical_request = (http_request_method + "\n" +
                             canonical_uri + "\n" +
                             canonical_querystring + "\n" +
                             canonical_headers + "\n" +
                             signed_headers + "\n" +
                             hashed_request_payload)

        # ************* 步骤 2：拼接待签名字符串 *************
        credential_scope = date + "/" + service + "/" + "tc3_request"
        hashed_canonical_request = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
        string_to_sign = (self.algorithm + "\n" +
                          str(timestamp) + "\n" +
                          credential_scope + "\n" +
                          hashed_canonical_request)

        # ************* 步骤 3：计算签名 *************
        secret_date = self._sign(("TC3" + self.secret_key).encode("utf-8"), date)
        secret_service = self._sign(secret_date, service)
        secret_signing = self._sign(secret_service, "tc3_request")
        signature = hmac.new(secret_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

        # ************* 步骤 4：拼接 Authorization *************
        authorization = (self.algorithm + " " +
                         "Credential=" + self.secret_id + "/" + credential_scope + ", " +
                         "SignedHeaders=" + signed_headers + ", " +
                         "Signature=" + signature)
        return authorization, timestamp

    def send(self):
        authorization, timestamp = self._get_authorization()
        headers = {
            "Authorization": authorization,
            "Content-Type": "application/json; charset=utf-8",
            "Host": self.host,
            "X-TC-Action": self.action,
            "X-TC-Timestamp": timestamp,
            "X-TC-Version": "2020-10-02",
            "X-TC-Region": "ap-guangzhou"
        }
        connection = HTTPSConnection(self.host)
        connection.request("POST", "/", headers=headers, body=self.payload.encode("utf-8"))
        response = connection.getresponse()
        json_response = json.loads(response.read().decode())
        error = json_response.get('Response').get('Error')
        if error:
            print(self.username, error)


def _get_success_content(username: str, course_name: str) -> str:
    """Reading and rendering the HTML mail content."""
    with open('./snatcher/postman/files/mail.html', encoding='utf8') as f:
        html_file = f.read()
        template = Template(html_file)
        return template.render(username=username, course_name=course_name)


class EmailSenderFactory:
    @classmethod
    def get_email_sender(cls, sender_type: str, **kwargs) -> AbstractEmailSender:
        sender_class = None
        match sender_type:
            case 'text':
                sender_class = TextEmailSender
            case 'html':
                sender_class = HTMLEmailSender
            case 'tencent_cloud':
                sender_class = TencentCloudEmailSender
        return sender_class(**kwargs)


def send_email(
    receiver_email: str,
    username: str,
    course_name: str,
    total: int = -1,
    current: int = -1,
    success: bool = True,
    failed_reason: str = None
):
    content = ''
    if success:
        subject = '恭喜你，选课成功！!'
        if settings.USE_TENCENT_CLOUD_MAIL_SERVICE:
            sender_type = 'tencent_cloud'
        else:
            content = _get_success_content(username, course_name)
            sender_type = 'html'
    else:
        progress = f'%d / %d' % (current, total)
        subject = '选课失败通知'
        content = "学号为 %s 的意向课程 <%s> 选课失败，原因：%s。进度：%s" % (username, course_name, failed_reason, progress)
        sender_type = 'text'

    try:
        sender = EmailSenderFactory.get_email_sender(
            sender_type,
            receiver=receiver_email,
            subject=subject,
            content=content,
            username=username,
            course_name=course_name
        )
        sender.send()
    except Exception as exception:
        return 0, str(exception)
    return 1, ''


if __name__ == '__main__':
    send_email('1834763300@qq.com', '2204425143', '人工智能应用零基础入门与零代码实战+无人驾驶实训营', True)
