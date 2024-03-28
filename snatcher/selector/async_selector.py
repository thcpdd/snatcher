"""
The asynchronous course selector in the module.
All asynchronous course selectors will use `aiohttp` package to send request.
"""
import re

import aiohttp
import asyncio
from asyncio import TimeoutError
from aiohttp.client_exceptions import ContentTypeError

from .base import CourseSelector
# from ..db.mysql import (
#     query_pc_course_id,
#     query_pe_course_id,
# )
from ..session import get_session_manager


class AsynchronousCourseSelector(CourseSelector):
    async def set_jxb_ids(self):
        self.get_jxb_ids_data['xkkz_id'] = self.xkkz_id
        self.get_jxb_ids_data['kch_id'] = self.kch_id
        self.get_jxb_ids_data['kklxdm'] = self.course_type
        response = await self.session.post(self.jxb_ids_api, data=self.get_jxb_ids_data)
        json_data = await response.json()
        try:
            self.jxb_ids = json_data[0]['do_jxb_id']
        except IndexError:
            self.log.set_others('step-3_error_in_set_jxb_ids', '表单数据异常')
            self.mark_failed('表单数据异常')
        except ContentTypeError:
            self.log.set_others('step-3_error_in_set_jxb_ids', 'json解码失败')
            self.mark_failed('json解码失败')
        except TypeError:
            self.log.set_others('step-3_error_in_set_jxb_ids', '非法请求')
            self.mark_failed('非法请求')

    async def prepare_for_selecting(self):
        await self.set_kch_id()
        if self.kch_id is None:
            self.log.set('step-1_kch_id', 0)
            return 0
        self.log.set('step-1_kch_id', 1)

        await self.set_xkkz_id()
        if self.xkkz_id is None:
            self.log.set('step-2_xkkz_id', 0)
            return 0
        self.log.set('step-2_xkkz_id', 1)

        await self.set_jxb_ids()
        if self.jxb_ids is None:
            self.log.set('step-3_jxb_ids', 0)
            return 0
        self.log.set('step-3_jxb_ids', 1)
        return 1

    async def simulate_request(self):
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        self.session = aiohttp.ClientSession(cookies=self.cookies, timeout=timeout)
        success = await self.prepare_for_selecting()
        if not success:
            await self.session.close()
            return 0
        self.select_course_data['kch_id'] = self.kch_id
        self.select_course_data['jxb_ids'] = self.jxb_ids
        response = await self.session.post(self.select_course_api, data=self.select_course_data)
        try:
            json_data = await response.json()
        except ContentTypeError:
            self.log.set_others('step-4_json_decode_error_in_select', '选课异常')
            self.mark_failed('选课异常')
            return 0
        else:
            if json_data['flag'] == '1':
                self.log.set_others('step-4', '选课成功')
                return 1
            self.log.set_others('step-4_server_response', json_data['msg'])
            self.mark_failed(json_data['msg'])
            return -2
        finally:
            response.close()
            await self.session.close()

    async def async_select(self):
        manager = get_session_manager(self.username)
        retry = 0
        while retry < 3:
            cookie_string, port = manager.get_random_session()
            self.update_or_set_cookie(cookie_string, port)
            try:
                result = await self.simulate_request()
            except TimeoutError:
                self.log.timeout()
            else:
                if result == 1:
                    self.log.set_others('task_status', f'{self.real_name} 成功')
                    return 1
                if result == -2:
                    self.log.set_others('task_status', f'{self.real_name} 失败')
                    return 0
            self.log.retry()
            retry += 1
        self.log.set_others('task_status', f'{self.real_name} 失败')
        self.mark_failed('超出最大重试次数')
        return 0

    def select(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(self.async_select())


class AsynchronousPublicChoiceCourseSelector(AsynchronousCourseSelector):
    course_type = '10'  # 公选课

    # async def set_kch_id(self):
    #     course_id, course_name = query_pc_course_id(self.filter_condition)
    #     if not all([course_name, course_id]):
    #         return
    #     self.kch_id = course_id
    #     self.real_name = course_name
    #     self.log.set_others('step-0_found_course', course_name)

    async def set_xkkz_id(self):
        async with await self.session.get(self.index_url) as response:
            html = await response.text()
        regex = re.compile('<input type="hidden" name="firstXkkzId" id="firstXkkzId" value="(.*?)"/>')
        find_list = regex.findall(html)
        self.xkkz_id = find_list[0] if find_list else None


class AsynchronousPhysicalEducationCourseSelector(AsynchronousCourseSelector):
    course_type = '05'  # 体育课

    # async def set_kch_id(self):
    #     course_id, course_name = query_pe_course_id(int(self.parser.year), self.filter_condition)
    #     if not all([course_name, course_id]):
    #         return
    #     self.kch_id = course_id
    #     self.real_name = course_name
    #     self.log.set_others('step-0_found_course', course_name)

    async def set_xkkz_id(self):
        response = await self.session.get(self.index_url)
        html = await response.text()
        regex = re.compile(r"""<a id="tab_kklx_05".*?"queryCourse\(.*?,'05','(.*?)','.*?','.*?'\)".*?>体育分项</a>""",
                           re.S)
        search_list = regex.search(html)
        self.xkkz_id = search_list.groups()[0] if search_list else None
