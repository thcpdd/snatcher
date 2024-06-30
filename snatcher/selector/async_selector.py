"""
The asynchronous course selector in the module.
All asynchronous course selectors will use `aiohttp` package to send request.
"""
import re
import asyncio

import aiohttp
from aiohttp.client_exceptions import ContentTypeError

from snatcher.session import get_session_manager
from .base import CourseSelector, AsyncRuntimeLogger


class AsynchronousCourseSelector(CourseSelector):
    async def set_jxb_ids(self):
        self.get_jxb_ids_data['xkkz_id'] = self.xkkz_id
        self.get_jxb_ids_data['kch_id'] = self.kch_id
        self.get_jxb_ids_data['kklxdm'] = self.course_type

        response = await self.session.post(self.jxb_ids_api, data=self.get_jxb_ids_data)

        message = ''
        try:
            json_data = await response.json()
            self.jxb_ids = json_data[0]['do_jxb_id']
        except IndexError:
            message = '表单数据异常'
        except ContentTypeError:
            message = 'json解码失败'
        except TypeError:
            message = '非法请求'

        if message:
            await self.logger.set('step-3', message=message)
            self.mark_failed(message)

    async def prepare_for_selecting(self):
        await self.logger.set('step-1', 1)

        cache_xkkz_id = self.session_manager.get_xkkz_id(self.course_type)
        if cache_xkkz_id:
            self.xkkz_id = cache_xkkz_id
        else:
            await self.set_xkkz_id()

        if self.xkkz_id is None:
            await self.logger.set('step-2', 0)
            return 0
        await self.logger.set('step-2', 1)
        self.session_manager.save_xkkz_id(self.xkkz_id, self.course_type)

        await self.set_jxb_ids()
        if self.jxb_ids is None:
            await self.logger.set('step-3', 0)
            return 0
        await self.logger.set('step-3', 1)
        return 1

    async def simulate_request(self):
        async with aiohttp.ClientSession(timeout=self.timeout, cookies=self.cookies) as self.session:
            success = await self.prepare_for_selecting()
            if not success:
                return 0
            self.select_course_data['kch_id'] = self.kch_id
            self.select_course_data['jxb_ids'] = self.jxb_ids
            response = await self.session.post(self.select_course_api, data=self.select_course_data)
            try:
                json_data = await response.json()
            except ContentTypeError:
                await self.logger.set('step-4', message='选课异常')
                self.mark_failed('选课异常')
                return 0
            else:
                if json_data['flag'] == '1':
                    await self.logger.set('step-4', message='选课成功')
                    return 1
                await self.logger.set('step-4', message=json_data['msg'])
                self.mark_failed(json_data['msg'])
                return -2

    async def select(self):
        if self.session_manager is None:
            self.session_manager = get_session_manager(self.username)
        if isinstance(self.timeout, int):
            self.timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with AsyncRuntimeLogger(self.logger_key) as self.logger:
            retry = 0
            while retry < 3:
                cookie_string, port = self.session_manager.get_random_session()
                self.update_or_set_cookie(cookie_string, port)
                try:
                    result = await self.simulate_request()
                except Exception as exception:
                    await self.logger.set('step-4', message=str(exception))
                    await self.logger.retry()
                    retry += 1
                    await asyncio.sleep(20)
                else:
                    if result == 1:
                        return 1
                    return 0
            self.mark_failed('超出最大重试次数')
            return 0


class AsynchronousPublicChoiceCourseSelector(AsynchronousCourseSelector):
    course_type = '10'  # 公选课

    async def set_xkkz_id(self):
        async with await self.session.get(self.index_url) as response:
            html = await response.text()
        regex = re.compile(
            r"""<a id="tab_kklx_10".*?"queryCourse\(.*?,'10','(.*?)','.*?','.*?'\)".*?>通识选修课</a>""")
        find_list = regex.findall(html)
        if not find_list:
            regex = re.compile('<input type="hidden" name="firstXkkzId" id="firstXkkzId" value="(.*?)"/>')
            find_list = regex.findall(html)
        self.xkkz_id = find_list[0] if find_list else None


class AsynchronousPhysicalEducationCourseSelector(AsynchronousCourseSelector):
    course_type = '05'  # 体育课

    async def set_jxb_ids(self):
        self.get_jxb_ids_data.update({
            'zyfx_id': '666',
            'bh_id': '666',
            'xbm': '666',
            'xslbdm': '666',
            'mzm': '666',
            'xz': '666',
            'ccdm': '666',
            'xsbj': '666',
            'xqh_id': '666',
            'jg_id': '206',
        })
        await super().set_jxb_ids()

    async def set_xkkz_id(self):
        response = await self.session.get(self.index_url)
        html = await response.text()
        regex = re.compile(r"""<a id="tab_kklx_05".*?"queryCourse\(.*?,'05','(.*?)','.*?','.*?'\)".*?>体育分项</a>""",
                           re.S)
        search_list = regex.search(html)
        self.xkkz_id = search_list.groups()[0] if search_list else None
