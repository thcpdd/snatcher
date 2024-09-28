MessageType = tuple[int, str]


class Messages:
    KCH_ID_SUCCESS = (1, 'kch_id成功')
    KCH_ID_FAILED = (0, 'kch_id失败')
    XKKZ_ID_SUCCESS = (1, 'xkkz_id成功')
    XKKZ_ID_FAILED = (0, 'xkkz_id失败')
    JXB_IDS_SUCCESS = (1, 'jxb_ids成功')
    JXB_IDS_FAILED = (1, 'jxb_ids失败')
    SELECT_COURSE_SUCCESSFUL = (1, '选课成功')
    SELECT_COURSE_ERROR = (0, '选课异常')
    FORM_DATA_ERROR = (0, '表单数据异常')
    ILLEGAL_REQUEST = (0, '非法请求')
    OVER_MAXIMUM_RETRY_TIMES = (0, '超出最大重试次数')
    JSON_DECODED_FAILED = (0, 'JSON解码失败')
    JG_ID_FAILED = (0, 'jg_id失败')
    FOUND_JXB_FAILED = (0, '未找到相应教学班')
