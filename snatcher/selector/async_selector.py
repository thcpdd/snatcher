"""
The asynchronous course selector in the module.
All asynchronous course selectors will use `aiohttp` package to send request.
"""
import re
import asyncio

from aiohttp.client_exceptions import ContentTypeError

from .base import BaseCourseSelector, logging, MessageType, Messages


class AsyncCourseSelector(BaseCourseSelector):
    @logging
    async def set_jxb_ids(self) -> MessageType:
        self._construct_jxb_ids_params()

        response = await self.session.post(self.jxb_ids_api, data=self.get_jxb_ids_data)

        try:
            do_jxb_id_list = await response.json()
        except ContentTypeError:
            return Messages.JSON_DECODED_FAILED

        if isinstance(do_jxb_id_list, str):  # '0'
            return Messages.ILLEGAL_REQUEST

        if not do_jxb_id_list:  # []
            return Messages.FORM_DATA_ERROR

        return self._set_jxb_ids(do_jxb_id_list)

    @logging
    async def select_course(self) -> MessageType:
        self.select_course_data['kch_id'] = self.kch_id
        self.select_course_data['jxb_ids'] = self.jxb_ids

        response = await self.session.post(self.select_course_api, data=self.select_course_data)

        try:
            json_data = await response.json()
        except ContentTypeError:
            return Messages.SELECT_COURSE_ERROR

        if json_data['flag'] == '1':
            return Messages.SELECT_COURSE_SUCCESSFUL
        return 0, json_data['msg']

    async def _select(self) -> MessageType:
        code, message = await self.set_kch_id()
        if not code:
            return code, message

        code, message = await self.set_xkkz_id()
        if not code:
            return code, message

        code, message = await self.set_jxb_ids()
        if not code:
            return code, message

        return await self.select_course()

    async def select(self) -> MessageType:
        for _ in range(3):
            self.update_cookie()

            try:
                code, message = await self._select()
            except Exception as exception:
                await self.logger.set('error', message=str(exception))
                await self.logger.retry()
                await asyncio.sleep(5)
                continue

            return code, message
        return Messages.OVER_MAXIMUM_RETRY_TIMES


class AsyncPCSelector(AsyncCourseSelector):
    course_type = '10'  # 公选课

    @logging
    async def set_xkkz_id(self) -> MessageType:
        if self.xkkz_id:
            return Messages.XKKZ_ID_SUCCESS
        cache_xkkz_id = self.session_manager.get_xkkz_id(self.course_type)
        if cache_xkkz_id:
            self.xkkz_id = cache_xkkz_id
            return Messages.XKKZ_ID_SUCCESS
        response = await self.session.get(self.index_url)
        html = await response.text()
        regex = re.compile(
            r"""<a id="tab_kklx_10".*?"queryCourse\(.*?,'10','(.*?)','.*?','.*?'\)".*?>通识选修课</a>""")
        find_list = regex.findall(html)
        if find_list:
            self.xkkz_id = find_list[0]
            self.session_manager.save_xkkz_id(self.xkkz_id, self.course_type)
            return Messages.XKKZ_ID_SUCCESS
        regex = re.compile('<input type="hidden" name="firstXkkzId" id="firstXkkzId" value="(.*?)"/>')
        find_list = regex.findall(html)
        if find_list:
            self.xkkz_id = find_list[0]
            self.session_manager.save_xkkz_id(self.xkkz_id, self.course_type)
            return Messages.XKKZ_ID_SUCCESS
        return Messages.XKKZ_ID_FAILED

    def _construct_jxb_ids_params(self):
        if not self.get_jxb_ids_data['xkkz_id']:
            self.get_jxb_ids_data['xkkz_id'] = self.xkkz_id
        self.get_jxb_ids_data['kch_id'] = self.kch_id

    def _set_jxb_ids(self, do_jxb_id_list: list[dict]) -> MessageType:
        if len(do_jxb_id_list) == 1:
            self.jxb_ids = do_jxb_id_list[0]['do_jxb_id']
        else:
            for do_jxb_id in do_jxb_id_list:
                if do_jxb_id['jxb_id'] == self.jxb_id:
                    self.jxb_ids = do_jxb_id['do_jxb_id']
                    break
            else:
                return Messages.FOUND_JXB_FAILED
        return Messages.JXB_IDS_SUCCESS


class AsyncPESelector(AsyncCourseSelector):
    course_type = '05'  # 体育课

    @logging
    async def set_xkkz_id(self) -> MessageType:
        if self.jg_id and self.xkkz_id:
            return Messages.XKKZ_ID_SUCCESS
        response = await self.session.get(self.index_url)
        html = await response.text()
        regex = re.compile(r"""<a id="tab_kklx_05".*?"queryCourse\(.*?,'05','(.*?)','.*?','.*?'\)".*?>体育分项</a>""",
                           re.S)
        search_list = regex.search(html)
        if not search_list:
            return Messages.XKKZ_ID_FAILED
        self.xkkz_id = search_list.groups()[0]

        find_list = re.findall('<input type="hidden" name="jg_id_1" id="jg_id_1" value="(.*?)"/>', html)
        if not find_list:
            return 0, Messages.JG_ID_FAILED
        self.jg_id = find_list[0]

        extra_params_names = ['bh_id', 'xbm', 'xslbdm', 'mzm', 'xz', 'ccdm', 'xsbj', 'zyfx_id']
        extra_jxb_ids_params = {'xqh_id': '3'}
        for name in extra_params_names:
            find_list = re.findall(f'<input type="hidden" name="{name}" id="{name}" value="(.*?)"/>', html)
            value = '6' if not find_list else find_list[0]
            extra_jxb_ids_params[name] = value
        self.extra_jxb_ids_params = extra_jxb_ids_params
        self.session_manager.save_xkkz_id(self.xkkz_id, self.course_type)
        return Messages.XKKZ_ID_SUCCESS

    def _construct_jxb_ids_params(self):
        if not self.get_jxb_ids_data['xkkz_id']:
            self.get_jxb_ids_data['xkkz_id'] = self.xkkz_id
            self.get_jxb_ids_data['jg_id'] = self.jg_id
            self.get_jxb_ids_data.update(self.extra_jxb_ids_params)
        self.get_jxb_ids_data['kch_id'] = self.kch_id

    def _set_jxb_ids(self, do_jxb_id_list: list[dict]) -> MessageType:
        self.jxb_ids = do_jxb_id_list[0]['do_jxb_id']
        return Messages.JXB_IDS_SUCCESS
