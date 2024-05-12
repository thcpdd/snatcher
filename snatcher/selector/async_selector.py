"""
The asynchronous course selector in the module.
All asynchronous course selectors will use `aiohttp` package to send request.
"""
import re

import aiohttp
from aiohttp.client_exceptions import (
    ContentTypeError,
    ClientConnectorError,
)

from snatcher.session import get_session_manager
from .base import CourseSelector, AsyncRunningLogger


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
            await self.log.set_others('step-3_error_in_set_jxb_ids', '表单数据异常')
            self.mark_failed('表单数据异常')
        except ContentTypeError:
            await self.log.set_others('step-3_error_in_set_jxb_ids', 'json解码失败')
            self.mark_failed('json解码失败')
        except TypeError:
            await self.log.set_others('step-3_error_in_set_jxb_ids', '非法请求')
            self.mark_failed('非法请求')

    async def prepare_for_selecting(self):
        await self.log.set_others('step-0_found_course', self.real_name)
        await self.log.set('step-1_kch_id', 1)

        cache_xkkz_id = self.session_manager.get_xkkz_id()
        if cache_xkkz_id:
            self.xkkz_id = cache_xkkz_id
        else:
            await self.set_xkkz_id()

        if self.xkkz_id is None:
            await self.log.set('step-2_xkkz_id', 0)
            return 0
        await self.log.set('step-2_xkkz_id', 1)
        self.session_manager.save_xkkz_id(self.xkkz_id)

        await self.set_jxb_ids()
        if self.jxb_ids is None:
            await self.log.set('step-3_jxb_ids', 0)
            return 0
        await self.log.set('step-3_jxb_ids', 1)
        return 1

    async def simulate_request(self):
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
        self.session.cookie_jar.update_cookies(self.cookies)
        success = await self.prepare_for_selecting()
        if not success:
            self.mark_failed('选课参数不完整')
            await self.session.close()
            return 0
        self.select_course_data['kch_id'] = self.kch_id
        self.select_course_data['jxb_ids'] = self.jxb_ids
        response = await self.session.post(self.select_course_api, data=self.select_course_data)
        try:
            json_data = await response.json()
        except ContentTypeError:
            await self.log.set_others('step-4_json_decode_error_in_select', '选课异常')
            self.mark_failed('选课异常')
            return 0
        else:
            if json_data['flag'] == '1':
                await self.log.set_others('step-4', '选课成功')
                return 1
            await self.log.set_others('step-4_server_response', json_data['msg'])
            self.mark_failed(json_data['msg'])
            return -2
        finally:
            response.close()
            await self.session.close()

    async def select(self):
        if self.session_manager is None:
            self.session_manager = get_session_manager(self.username)
        async with AsyncRunningLogger(self.log_key) as self.log:
            retry = 0
            while retry < 3:
                cookie_string, port = self.session_manager.get_session_by_weight()
                self.update_or_set_cookie(cookie_string, port)
                try:
                    result = await self.simulate_request()
                except (TimeoutError, ClientConnectorError):
                    await self.log.retry()
                    retry += 1
                except Exception as exception:
                    await self.log.set_others('step-4_error_in_select', str(exception))
                    self.mark_failed(str(exception))
                    return 0
                else:
                    if result == 1:
                        await self.log.set_others('task_status', f'{self.real_name} 成功')
                        return 1
                    return 0
            self.mark_failed('超出最大重试次数')
            return 0


class AsynchronousPublicChoiceCourseSelector(AsynchronousCourseSelector):
    course_type = '10'  # 公选课

    async def set_xkkz_id(self):
        async with await self.session.get(self.index_url) as response:
            html = await response.text()
        regex = re.compile('<input type="hidden" name="firstXkkzId" id="firstXkkzId" value="(.*?)"/>')
        find_list = regex.findall(html)
        if not find_list:
            # 尝试第二种匹配（有别的选修课的时候）
            regex = re.compile(
                r"""<a id="tab_kklx_10".*?"queryCourse\(.*?,'10','(.*?)','.*?','.*?'\)".*?>通识选修课</a>"""
            )
            find_list = regex.findall(html)
        self.xkkz_id = find_list[0] if find_list else None


class AsynchronousPhysicalEducationCourseSelector(AsynchronousCourseSelector):
    course_type = '05'  # 体育课

    async def set_xkkz_id(self):
        response = await self.session.get(self.index_url)
        html = await response.text()
        regex = re.compile(r"""<a id="tab_kklx_05".*?"queryCourse\(.*?,'05','(.*?)','.*?','.*?'\)".*?>体育分项</a>""",
                           re.S)
        search_list = regex.search(html)
        self.xkkz_id = search_list.groups()[0] if search_list else None
