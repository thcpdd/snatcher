import re

from requests import session
from requests.exceptions import JSONDecodeError, ReadTimeout

from ..session import get_session_manager
from .base import CourseSelector
from ..db.mysql import (
    create_failed_data,
    query_pc_course_id,
    query_pe_course_id
)


class SynchronousCourseSelector(CourseSelector):
    def set_jxb_ids(self):
        self.get_jxb_ids_data['xkkz_id'] = self.xkkz_id
        self.get_jxb_ids_data['kch_id'] = self.kch_id
        self.get_jxb_ids_data['kklxdm'] = self.course_type
        response = self.session.post(
            self.jxb_ids_api,
            data=self.get_jxb_ids_data,
            timeout=self.timeout,
        )
        try:
            json_data = response.json()
            self.jxb_ids = json_data[0]['do_jxb_id']
        except IndexError:
            self.log.set_others('step-3_error_in_set_jxb_ids', '表单数据异常')
            create_failed_data(self.username, self.real_name, self.log.key, '表单数据异常')
        except JSONDecodeError:
            self.log.set_others('step-3_error_in_set_jxb_ids', 'json解码失败')
            create_failed_data(self.username, self.real_name, self.log.key, 'json解码失败')
        except TypeError:
            self.log.set_others('step-3_error_in_set_jxb_ids', '非法请求')
            create_failed_data(self.username, self.real_name, self.log.key, '非法请求')

    def prepare_for_selecting(self):
        self.set_kch_id()
        if self.kch_id is None:
            self.log.set('step-1_kch_id', 0)
            return 0
        self.log.set('step-1_kch_id', 1)

        self.set_xkkz_id()
        if self.xkkz_id is None:
            self.log.set('step-2_xkkz_id', 0)
            return 0
        self.log.set('step-2_xkkz_id', 1)

        self.set_jxb_ids()
        if self.jxb_ids is None:
            self.log.set('step-3_jxb_ids', 0)
            return 0
        self.log.set('step-3_jxb_ids', 1)
        return 1

    def simulate_request(self):
        self.session = session()
        self.session.cookies.update(self.cookies)
        success = self.prepare_for_selecting()
        if not success:
            return 0
        self.select_course_data['kch_id'] = self.kch_id
        self.select_course_data['jxb_ids'] = self.jxb_ids
        response = self.session.post(
            self.select_course_api,
            data=self.select_course_data,
            timeout=self.timeout
        )
        try:
            json_data = response.json()
            if json_data['flag'] == '1':
                self.log.set_others('step-4', '选课成功')
                return 1
            self.log.set_others('step-4_server_response', json_data['msg'])
            create_failed_data(self.username, self.real_name, self.log.key, json_data['msg'])
            return -2
        except JSONDecodeError:
            self.log.set_others('step-4_json_decode_error_in_select', '选课异常')
            create_failed_data(self.username, self.real_name, self.log.key, '选课异常')
            return 0

    def select(self):
        manager = get_session_manager(self.username)
        retry = 0
        while retry < 3:
            cookie_string, port = manager.get_random_session()
            self.update_or_set_cookie(cookie_string, port)
            try:
                result = self.simulate_request()
            except ReadTimeout:
                self.log.timeout()
            else:
                if result == 1:
                    self.log.set_others('task_status', f'{self.filter_condition} 成功')
                    return 1
                if result == -2:
                    self.log.set_others('task_status', f'{self.filter_condition} 失败')
                    return 0
            self.log.retry()
            retry += 1
        self.log.set_others('task_status', f'{self.filter_condition} 失败')
        create_failed_data(self.username, self.real_name, self.log.key, '超出最大重试次数')
        return 0


class SynchronousPublicChoiceCourseSelector(SynchronousCourseSelector):
    course_type = '10'  # 公选课

    def set_kch_id(self):
        course_id, course_name = query_pc_course_id(self.filter_condition)
        if not all([course_name, course_id]):
            return
        self.kch_id = course_id
        self.real_name = course_name
        self.log.set_others('step-0_found_course', course_name)

    def set_xkkz_id(self):
        html = self.session.get(self.index_url, timeout=self.timeout).text
        # regex = re.compile('<input type="hidden" name="firstXkkzId" id="firstXkkzId" value="(.*?)"/>')
        regex = re.compile(r"""<a id="tab_kklx_10".*?"queryCourse\(.*?,'10','(.*?)','.*?','.*?'\)".*?>通识选修课</a>""")
        find_list = regex.findall(html)
        self.xkkz_id = find_list[0] if find_list else None


class SynchronousPhysicalEducationCourseSelector(SynchronousCourseSelector):
    course_type = '05'  # 体育课

    def set_kch_id(self):
        course_id, course_name = query_pe_course_id(int(self.parser.year), self.filter_condition)
        if not all([course_name, course_id]):
            return
        self.kch_id = course_id
        self.real_name = course_name
        self.log.set_others('step-0_found_course', course_name)

    def set_xkkz_id(self):
        html = self.session.get(self.index_url, timeout=self.timeout).text
        regex = re.compile(r"""<a id="tab_kklx_05".*?"queryCourse\(.*?,'05','(.*?)','.*?','.*?'\)".*?>体育分项</a>""",
                           re.S)
        search_list = regex.search(html)
        self.xkkz_id = search_list.groups()[0] if search_list else None

# class SynchronousEnglishCourseSelector(SynchronousCourseSelector):
#     course_type = '01'  # 主修课程
#
#     def __init__(self, filter_condition: str, username: str, cookie_string, port, section='星期一第1-2'):
#         """
#         :param filter_condition: 查询条件
#         :param username: 学号
#         :param section: 第几节英语课
#         """
#         super().__init__(filter_condition, username, cookie_string, port)
#         self.search_course_api = self.base_url + '/xsxk/zzxkyzb_cxZzxkYzbPartDisplay.html?gnmkdm=N253512'
#         self.section = section
#
#     def search_course(self):
#         data = self.get_jxb_ids_data.copy()
#         data['kspage'] = 1
#         data['jspage'] = 10
#         data['kklxdm'] = '01'
#         response = self.session.post(self.search_course_api, data=data)
#         for json_data in response.json()['tmpList']:
#             print(json_data)
#
#     def set_kch_id(self):
#         self.kch_id = 'E0C14E34FA15301BE0530284030AC4CF'
#
#     def set_xkkz_id(self):
#         self.xkkz_id = '0DED336E5061CC2AE0630284030A0FB8'