from pydantic import BaseModel


class ResponseCodes:
    OK = (1, 'OK')
    INVALID_FUEL = (100, '无效的燃料，火箭启动失败')
    FUEL_IS_USING = (105, '燃料正在被使用中……')
    FUEL_WAS_USED = (110, '燃料已被耗尽')
    ILLEGAL_REQUEST = (200, '非法请求')
    INVALID_IDENTITY = (205, '身份无效')
    INVALID_TOKEN = (210, '凭证无效')
    LOGIN_FAILED = (215, '登录失败')
    LOGIN_SUCCESS = (220, '登录失败')


def tuple2dict(message_tuple: tuple[int, str]):
    code, message = message_tuple
    return {'code': code, 'message': message}


class SnatcherResponse(BaseModel):
    code: int
    message: str
    data: dict | list | None

    def __init__(self, message_tuple: tuple[int, str], data: dict | list | None = None):
        code, message = message_tuple
        super().__init__(code=code, message=message, data=data)
