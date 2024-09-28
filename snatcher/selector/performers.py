"""
Course selector performers here:
    All course selector will be proxy call by performer.
"""
import asyncio
from datetime import datetime

from redis.asyncio import Redis
from redis.client import PubSub

from snatcher.storage.mongo import collections, BSONObjectId, update_fuel_status
from snatcher.postman.mail import send_email
from snatcher.session import async_check_and_set_session
from snatcher.storage.cache import parse_message, CHANNEL_NAME
from .async_selector import AsyncCourseSelector


async def async_selector_performer(
    selector_class: type[AsyncCourseSelector],
    username: str,
    email: str,
    fuel_id: str,
    goals: list[tuple[str, str, str]],
):
    """Proxying call and perform the course_selector."""
    submitted_collection = collections['submitted']
    failure_collection = collections['failure']
    total = len(goals)

    async with selector_class(username, fuel_id) as selector:
        fuel_id = BSONObjectId(fuel_id)

        for course_name, course_id, jxb_id in goals:
            log_key = username + '-' + course_name
            row_id = submitted_collection.create(
                username=username,
                email=email,
                course_name=course_name,
                log_key=log_key
            )
            await selector.update_selector_info(course_name, course_id, jxb_id, log_key)

            code, message = await selector.select()

            if code == 1:
                update_fuel_status(fuel_id, status='used')
                submitted_collection.update(row_id, success=1)
                success, exception = send_email(email, username, course_name)
                if not success:
                    print(f'邮件发送失败：{username}-{course_name}', exception)
                break

            failure_collection.create(
                username=username,
                course_name=course_name,
                log_key=log_key,
                reason=message,
                port=int(selector.port)
            )
            send_email(
                '1834763300@qq.com',
                username,
                course_name,
                total=total,
                current=selector.index - 1,
                success=False,
                failed_reason=message
            )
        else:
            update_fuel_status(fuel_id, status='unused')


class SimpleSelectorPerformer:
    def __init__(
        self,
        username: str,
        password: str,
        selector_class: type[AsyncCourseSelector],
        goals: list[tuple[str, str, str]],
    ) -> None:
        self.selector_class = selector_class
        self.username = username
        self.password = password
        self.goals = goals
        self.p: PubSub | None = None

    async def select_course(self):
        success = await async_check_and_set_session(self.username, self.password)
        if not success:
            print('登录失败，请检查学号密码是否正确')
            raise asyncio.CancelledError
        async with self.selector_class(self.username) as selector:
            for course_name, course_id, jxb_id in self.goals:
                await selector.update_selector_info(course_name, course_id, jxb_id)
                code, message = await selector.select()
                if code == 1:
                    break
        raise asyncio.CancelledError

    async def print_log(self):
        print('正在选课中……请勿退出程序！')
        print('日志信息：')

        while True:
            message = await self.p.parse_response()
            print(datetime.now(), parse_message(message[-1]))

    async def startup(self):
        print('正在与 Redis 建立连接……')
        conn = Redis(decode_responses=True)
        print('订阅日志消息')
        self.p = conn.pubsub()
        await self.p.subscribe(CHANNEL_NAME)
        await self.p.parse_response()

        try:
            await asyncio.gather(
                asyncio.create_task(self.select_course()),
                asyncio.create_task(self.print_log())
            )
        except asyncio.CancelledError:
            print('正在释放资源……')
            await self.p.unsubscribe()
            await conn.aclose()
            print('资源释放完毕')

    def perform(self):
        asyncio.run(self.startup())
