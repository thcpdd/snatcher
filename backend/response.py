from typing import Any

from fastapi.responses import JSONResponse


class ResponseCodes:
    OK = (1, 'OK')
    FREQUENT_REQUEST = (5, '请勿频繁发起请求')
    INPUT_DATA_INVALID = (10, '输入数据验证失败')
    INVALID_FUEL = (100, '无效的燃料，火箭启动失败')
    FUEL_IS_USING = (105, '燃料正在被使用中……')
    FUEL_WAS_USED = (110, '燃料已被耗尽')
    NOT_IN_VALID_TIME = (115, '系统暂未开放')
    OVER_MAX_COURSE_NUMBER = (120, '意向课程总数不能超过5个')
    ILLEGAL_REQUEST = (200, '非法请求')
    INVALID_IDENTITY = (205, '身份无效')
    INVALID_TOKEN = (210, '凭证无效')
    LOGIN_FAILED = (215, '登录失败')
    LOGIN_SUCCESS = (220, '登录成功')


def tuple2dict(message_tuple: tuple[int, str]):
    code, message = message_tuple
    return {'code': code, 'message': message}


class SnatcherResponse(JSONResponse):
    def __init__(self, message_tuple: tuple[int, str], data: Any = None, *args, **kwargs):
        content = {
            'code': message_tuple[0],
            'message': message_tuple[1],
            'data': data
        }
        super().__init__(content=content, *args, **kwargs)
