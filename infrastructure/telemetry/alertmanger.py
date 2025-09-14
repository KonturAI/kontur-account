import asyncio

import httpx
import openai
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from infrastructure.redis_client.redis_client import RedisClient


class AlertManager:
    def __init__(
            self,
            tg_bot_token: str,
            service_name: str,
            alert_tg_chat_id: int,
            alert_tg_chat_thread_id: int,
            grafana_url: str,
            monitoring_redis_host: str,
            monitoring_redis_port: int,
            monitoring_redis_db: int,
            monitoring_redis_password: str,
            openai_api_key: str = None,
    ):
        self.bot = Bot(tg_bot_token)
        self.alert_tg_chat_id = alert_tg_chat_id
        self.alert_tg_chat_thread_id = alert_tg_chat_thread_id
        self.grafana_url = grafana_url
        self.service_name = service_name
        self.redis_client = RedisClient(
            monitoring_redis_host,
            monitoring_redis_port,
            monitoring_redis_db,
            monitoring_redis_password
        )
        if openai_api_key:
            self.openai_client = openai.AsyncOpenAI(
                api_key=openai_api_key,
                http_client=httpx.AsyncClient(proxy="http://32uLYMeQ:jLaDv4WK@193.160.72.227:62940")
            )
        else:
            self.openai_client = None

    def send_error_alert(self, trace_id: str, span_id: str, traceback: str):
        loop = asyncio.get_running_loop()
        loop.create_task(self.__send_error_alert(trace_id, span_id, traceback))

    async def __send_error_alert(self, trace_id: str, span_id: str, traceback: str):
        alert_send = await self.redis_client.get(trace_id)
        if alert_send:
            return

        await self.redis_client.set(trace_id, "1", ttl=30)
        await self.__send_error_alert_to_tg(trace_id, span_id, traceback)

    async def __send_error_alert_to_tg(self, trace_id: str, span_id: str, traceback: str):
        log_link = f"{self.grafana_url}/explore?schemaVersion=1&panes=%7B%220pz%22:%7B%22datasource%22:%22loki%22,%22queries%22:%5B%7B%22refId%22:%22A%22,%22expr%22:%22%7Bservice_name%3D~%5C%22.%2B%5C%22%7D%20%7C%20trace_id%3D%60{trace_id}%60%20%7C%3D%20%60%60%22,%22queryType%22:%22range%22,%22datasource%22:%7B%22type%22:%22loki%22,%22uid%22:%22loki%22%7D,%22editorMode%22:%22code%22,%22direction%22:%22backward%22%7D%5D,%22range%22:%7B%22from%22:%22now-2d%22,%22to%22:%22now%22%7D%7D%7D&orgId=1"
        trace_link = f"{self.grafana_url}/explore?schemaVersion=1&panes=%7B%220pz%22:%7B%22datasource%22:%22tempo%22,%22queries%22:%5B%7B%22refId%22:%22A%22,%22datasource%22:%7B%22type%22:%22tempo%22,%22uid%22:%22tempo%22%7D,%22queryType%22:%22traceql%22,%22limit%22:20,%22tableType%22:%22traces%22,%22metricsQueryType%22:%22range%22,%22query%22:%22{trace_id}%22%7D%5D,%22range%22:%7B%22from%22:%22now-2d%22,%22to%22:%22now%22%7D%7D%7D&orgId=1"

        text = f"""Произошла ошибка в сервисе: <b>{self.service_name}</b>
TraceID: <code>{trace_id}</code>
SpanID: <code>{span_id}</code>"""

        if self.openai_client is not None:
            try:
                llm_analysis = await self.generate_analysis(traceback)

                text += f"\n\n<b>Анализ LLM:</b>\n{llm_analysis}"

            except Exception as e:
                pass

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Логи", url=log_link)],
            [InlineKeyboardButton(text="🔍 Трейс", url=trace_link)]
        ])

        await self.bot.send_message(
            self.alert_tg_chat_id,
            text,
            parse_mode="HTML",
            message_thread_id=self.alert_tg_chat_thread_id,
            reply_markup=keyboard
        )

    async def generate_analysis(
            self,
            traceback: str,
    ) -> str:
        try:
            system_prompt = (
                "Ты инженер по наблюдаемости. "
                "Ниже лог ошибки Python со стеком вызова. "
                "Опиши:\n"
                "1. Где именно возникла ошибка (файл, класс, метод)\n"
                "2. Какой тип ошибки и сообщение\n"
                "3. Как её можно исправить."
                "Формат ответа: текст для телеграм-бота"
            )

            history: list = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": traceback}
            ]


            response = await self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=history,
                    temperature=0.3,
                )
            llm_response = response.choices[0].message.content
            return llm_response

        except Exception as err:
            pass